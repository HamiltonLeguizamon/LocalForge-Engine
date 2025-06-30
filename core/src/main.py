import os
import logging
import yaml
import subprocess
import concurrent.futures
import datetime
import sys
import time
import json
import shlex
from typing import Callable, Dict, Any, Optional

# Import centralized logging
from core.src.utils.log_manager import setup_logging
from core.src.cli.cli_manager import CLIManager


def _execute_command_safe(command: str, env: Dict[str, str], **kwargs) -> subprocess.Popen:
    """
    Execute a command safely without shell=True when possible.
    
    Args:
        command: Command string to execute
        env: Environment variables
        **kwargs: Additional keyword arguments for subprocess.Popen
        
    Returns:
        subprocess.Popen: Process object
    """
    # Try to parse simple commands without shell=True
    try:
        # For simple commands (single command without pipes, redirects, etc.)
        # we can try to avoid shell=True
        if not any(char in command for char in ['|', '>', '<', '&', ';', '&&', '||', '`', '$(']):
            # Simple command, try to split it safely
            if os.name == 'nt':  # Windows
                # On Windows, we still need shell=True for many commands
                # but we can add timeout to prevent hanging
                kwargs['shell'] = True
            else:  # Unix-like systems
                # Try to split the command
                try:
                    cmd_list = shlex.split(command)
                    kwargs.pop('shell', None)  # Remove shell=True
                    return subprocess.Popen(cmd_list, env=env, **kwargs)
                except (ValueError, OSError):
                    # If splitting fails, fall back to shell=True
                    kwargs['shell'] = True
        else:
            # Complex command with pipes/redirects, need shell=True
            kwargs['shell'] = True
            
        return subprocess.Popen(command, env=env, **kwargs)
        
    except Exception:
        # If anything fails, fall back to the original approach
        kwargs['shell'] = True
        return subprocess.Popen(command, env=env, **kwargs)


class PipelineRunner:
    """Encapsulates the logic to execute a CI/CD pipeline."""
    
    def __init__(self, progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None):
        """
        Initializes the runner.

        Args:
            progress_callback: An optional function to call to report progress.
                              It should accept a dictionary with event details.
        """
        self.progress_callback = progress_callback
        self.stop_requested = False
        self.current_process = None
        
    def _emit_progress(self, event_data: Dict[str, Any]):
        """Calls the progress callback if defined."""
        if self.progress_callback:
            try:
                self.progress_callback(event_data)
            except Exception as e:
                logging.error(f"Error in progress callback: {e}")

    def stop(self):
        """Requests stopping the running pipeline."""
        logging.info("Pipeline stop requested")
        self.stop_requested = True
        
        # Terminate current process if it exists
        if self.current_process and self.current_process.poll() is None:
            try:
                logging.info("Terminating current process...")
                self.current_process.terminate()
                # Give a moment for clean termination
                try:
                    self.current_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # If it doesn't terminate cleanly, force termination
                    logging.warning("Forcing process termination...")
                    self.current_process.kill()
                    self.current_process.wait()
            except Exception as e:
                logging.error(f"Error terminating process: {e}")
        
        self._emit_progress({"event": "pipeline_stopped", "reason": "User requested stop"})

    def execute_step(self, step: Dict[str, Any], env_vars: Optional[Dict[str, str]] = None, is_cleanup: bool = False) -> Dict[str, Any]:
        """Executes an individual pipeline step."""
        step_name = step['step']
        logging.info(f"Executing step: {step_name}")
        print(f"Executing step: {step_name}")
        self._emit_progress({"event": "step_start", "step": step_name})

        env = os.environ.copy()
        if env_vars:
            env.update(env_vars)

        start_time = time.time()
        
        # Determine the commands to execute - support for both formats
        commands = []
        if 'commands' in step:
            # New format: list of commands
            commands = step['commands'] if isinstance(step['commands'], list) else [step['commands']]
        elif 'command' in step:
            # Legacy format: single command
            commands = [step['command']]
        else:
            error_msg = f"Step {step_name} has no 'command' or 'commands' defined"
            logging.error(error_msg)
            self._emit_progress({"event": "step_failure", "step": step_name, "error": error_msg})
            return {
                "step": step_name,
                "status": "error",
                "duration": "0.00s",
                "output": None,
                "error": error_msg            }            # Execute each command sequentially
        all_stdout = []
        all_stderr = []
        
        try:
            for i, command in enumerate(commands):                # Check if stop was requested (except for cleanup steps)
                if self.stop_requested and not is_cleanup:
                    logging.info(f"Stop requested, cancelling step {step_name}")
                    self._emit_progress({"event": "step_cancelled", "step": step_name, "reason": "Stop requested"})
                    return {
                        "step": step_name,
                        "status": "cancelled",
                        "duration": f"{time.time() - start_time:.2f}s",
                        "output": None,                        "error": "Cancelled by stop request"
                    }
                
                if len(commands) > 1:
                    logging.info(f"Executing command {i+1}/{len(commands)}: {command}")
                    self._emit_progress({"event": "step_output", "step": step_name, "output": f">>> Command {i+1}/{len(commands)}: {command}"})

                # Use Popen to capture output in real-time
                process = _execute_command_safe(
                    command,
                    env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1, # Line-buffered
                    universal_newlines=True,
                    encoding='utf-8',
                    errors='replace'  # Replace problematic characters instead of failing
                )
                  # Save reference to current process
                self.current_process = process

                # Read stdout and stderr
                stdout, stderr = process.communicate()
                return_code = process.returncode
                
                # Clear process reference
                self.current_process = None

                if stdout:
                    all_stdout.append(stdout.strip())
                    logging.info(f"Command {i+1} output in {step_name}:\n{stdout}")
                    self._emit_progress({"event": "step_output", "step": step_name, "output": stdout})

                if return_code != 0:
                    if stderr:
                        all_stderr.append(stderr.strip())
                        logging.error(f"Error in command {i+1} of {step_name}:\n{stderr}")
                        self._emit_progress({"event": "step_error", "step": step_name, "error": stderr})

                    # Throw exception to be caught below
                    raise subprocess.CalledProcessError(return_code, command, output=stdout, stderr=stderr)

            # If we get here, all commands executed successfully
            duration = time.time() - start_time
            combined_stdout = '\n'.join(all_stdout) if all_stdout else None
            
            logging.info(f"Step {step_name} completed successfully in {duration:.2f} seconds.")
            self._emit_progress({"event": "step_success", "step": step_name, "duration": f"{duration:.2f}s"})

            return {
                "step": step_name,
                "status": "success",
                "duration": f"{duration:.2f}s",
                "output": combined_stdout,
                "error": None
            }

        except subprocess.CalledProcessError as e:
            duration = time.time() - start_time
            combined_stderr = '\n'.join(all_stderr) if all_stderr else str(e)
            combined_stdout = '\n'.join(all_stdout) if all_stdout else None
            
            error_msg = f"Error executing step {step_name} (code: {e.returncode}): {e}"
            logging.error(error_msg)
            self._emit_progress({
                "event": "step_failure",
                "step": step_name,
                "duration": f"{duration:.2f}s",
                "error": combined_stderr
            })

            return {
                "step": step_name,
                "status": "error",
                "duration": f"{duration:.2f}s",
                "output": combined_stdout,
                "error": combined_stderr
            }
        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Unexpected error executing step {step_name}: {e}"
            logging.error(error_msg)
            self._emit_progress({
                "event": "step_failure",
                "step": step_name,
                "duration": f"{duration:.2f}s",
                "error": str(e)
            })
            return {
                "step": step_name,
                "status": "error",
                "duration": f"{duration:.2f}s",
                "output": None,
                "error": str(e)
            }

    def execute_pipeline(self, pipeline_file: str, parallel: bool = False, env_vars: Optional[Dict[str, str]] = None, continue_on_error: bool = False) -> bool:
        """Executes the complete pipeline."""
        self._emit_progress({"event": "pipeline_start", "pipeline_file": pipeline_file})
        
        # Get the pipeline file directory
        pipeline_dir = os.path.dirname(os.path.abspath(pipeline_file))
        original_cwd = os.getcwd()        
        try:
            # Change to pipeline directory to execute relative commands
            os.chdir(pipeline_dir)
            logging.info(f"Changing working directory to: {pipeline_dir}")
            
            with open(pipeline_file, 'r', encoding='utf-8') as file:
                pipeline_config = yaml.safe_load(file)
                
            os.makedirs("reports", exist_ok=True)
            pipeline_start_time = time.time()
            results = []
            final_success = True
            
            # Parallel execution
            if parallel and 'parallel_steps' in pipeline_config:
                logging.info("Starting parallel step execution")
                self._emit_progress({"event": "parallel_start"})
                parallel_steps = pipeline_config.get('parallel_steps', [])
                with concurrent.futures.ThreadPoolExecutor(max_workers=len(parallel_steps)) as executor:
                    futures = {executor.submit(self.execute_step, step, env_vars): step for step in parallel_steps}
                    for future in concurrent.futures.as_completed(futures):
                        step_info = futures[future]
                        try:
                            result = future.result()
                            results.append(result)
                            if result["status"] == "error":
                                final_success = False
                                if not continue_on_error:
                                    logging.error(f"Stopping pipeline due to error in parallel step: {result['step']}")
                                    self._emit_progress({"event": "pipeline_halted", "reason": f"Error in parallel step: {result['step']}"})
                                    # Cancel other futures (best effort)
                                    for f in futures:
                                        if not f.done():
                                            f.cancel()
                                    break # Exit the completed loop
                        except Exception as exc:
                            step_name = step_info.get('step', 'unknown')
                            logging.error(f'Parallel step {step_name} generated an exception: {exc}')
                            results.append({"step": step_name, "status": "error", "error": str(exc), "duration": "0s"})
                            final_success = False
                            if not continue_on_error:
                                self._emit_progress({"event": "pipeline_halted", "reason": f"Exception in parallel step: {step_name}"})
                                # Cancel other futures
                                for f in futures:
                                    if not f.done():
                                        f.cancel()
                                break
                self._emit_progress({"event": "parallel_end"})
                if not final_success and not continue_on_error:
                    # Save report and exit if there was an error and execution should not continue
                    self._save_report(pipeline_file, pipeline_start_time, results, final_success)
                    return False

            # Sequential execution
            if 'pipeline' in pipeline_config and (final_success or continue_on_error):
                logging.info("Starting sequential step execution")
                self._emit_progress({"event": "sequential_start"})
                for step in pipeline_config.get('pipeline', []):
                    result = self.execute_step(step, env_vars)
                    results.append(result)
                    if result["status"] == "error":
                        final_success = False
                        if not continue_on_error:
                            logging.error(f"Stopping pipeline due to error in step: {result['step']}")
                            self._emit_progress({"event": "pipeline_halted", "reason": f"Error in step: {result['step']}"})
                            break # Exit the sequential loop
                self._emit_progress({"event": "sequential_end"})

            # Execute cleanup steps if they exist
            if 'cleanup' in pipeline_config:
                logging.info("Starting cleanup steps")
                self._emit_progress({"event": "cleanup_start"})
                for cleanup_step in pipeline_config.get('cleanup', []):
                    cleanup_result = self.execute_step(cleanup_step, env_vars, is_cleanup=True)
                    results.append(cleanup_result)
                    # Cleanup steps don't affect the overall pipeline success
                self._emit_progress({"event": "cleanup_end"})

            # Save final report
            self._save_report(pipeline_file, pipeline_start_time, results, final_success)

            if not final_success:
                logging.error("Pipeline completed with errors")
                self._emit_progress({"event": "pipeline_finished", "success": False})
            else:
                logging.info("Pipeline completed successfully")
                self._emit_progress({"event": "pipeline_finished", "success": True})

            return final_success
            
        except Exception as e:
            logging.error(f"Error loading pipeline file {pipeline_file}: {e}")
            self._emit_progress({"event": "pipeline_error", "error": f"Error loading {pipeline_file}: {e}"})
            return False
        finally:
            # Restore original directory
            os.chdir(original_cwd)

    def _save_report(self, pipeline_file, start_time, results, success):
        """Saves the pipeline report in JSON format."""
        pipeline_duration = time.time() - start_time
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report = {
            "pipeline_file": pipeline_file,
            "start_time": datetime.datetime.fromtimestamp(start_time).strftime("%Y-%m-%d %H:%M:%S"),
            "duration": f"{pipeline_duration:.2f}s",
            "steps": results,
            "success": success
        }
        report_file = f"reports/pipeline_report_{timestamp}.json"
        try:
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            logging.info(f"Pipeline report saved to {report_file}")
            self._emit_progress({"event": "report_saved", "file": report_file})
        except Exception as e:
            logging.error(f"Error saving the report {report_file}: {e}")
            self._emit_progress({"event": "report_error", "error": str(e)})


def main():
    """Main function for entry points."""
    # Use centralized CLI
    parser = CLIManager.create_pipeline_parser()
    args = parser.parse_args()

    # Configure logging with centralized handler
    log_level = CLIManager.get_log_level(args.log_level)
    setup_logging(log_file="ci_cd_cli.log", level=log_level)

    # Parse environment variables
    env_vars = CLIManager.parse_env_vars(args.env)

    logging.info(f"Starting pipeline from CLI: {args.pipeline}")

    # Create runner instance (without callback for CLI)
    runner = PipelineRunner()

    success = runner.execute_pipeline(
        args.pipeline,
        parallel=args.parallel,
        env_vars=env_vars,
        continue_on_error=args.continue_on_error
    )

    sys.exit(0 if success else 1)


# --- Main block for command line execution ---
if __name__ == "__main__":
    main()

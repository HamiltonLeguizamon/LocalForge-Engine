#!/usr/bin/env python3
"""
Shortcut script to run the CI/CD engine from the project root.
Improved version that doesn't manipulate sys.path.
"""
import subprocess
import sys
import os
from pathlib import Path


def main():
    """Main function that runs the pipeline using the installed package."""
    try:
        # Try to use the installed package first
        result = subprocess.run([
            sys.executable, "-m", "core.src.main"
        ] + sys.argv[1:], cwd=Path(__file__).parent)
        sys.exit(result.returncode)
    except Exception:
        # Fallback: use direct import for development
        import sys
        import os
        
        # Only add to path if we're in development
        if not __package__:
            core_src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'core', 'src')
            sys.path.insert(0, core_src_path)
        
        try:
            from core.src.utils.log_manager import setup_logging
            from core.src.cli.cli_manager import CLIManager
            from core.src.main import PipelineRunner
            import logging
            
            # Use centralized CLI
            parser = CLIManager.create_pipeline_parser()
            args = parser.parse_args()
            
            # Configure logging with centralized handler
            log_level = CLIManager.get_log_level(args.log_level)
            setup_logging(log_file="ci_cd_cli.log", level=log_level)

            # Parse environment variables
            env_vars = CLIManager.parse_env_vars(args.env)

            # Convert relative path to absolute path from current directory
            pipeline_path = os.path.abspath(args.pipeline)
            logging.info(f"Starting pipeline from wrapper: {pipeline_path}")

            # Create runner instance (without callback for CLI)
            runner = PipelineRunner()

            success = runner.execute_pipeline(
                pipeline_path,
                parallel=args.parallel,
                env_vars=env_vars,
                continue_on_error=args.continue_on_error
            )

            sys.exit(0 if success else 1)
            
        except Exception as e:
            print(f"Error executing the pipeline: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    main()

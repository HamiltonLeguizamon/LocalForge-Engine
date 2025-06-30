"""
Module for pipeline management and state.
"""
import os
import time
import threading
from datetime import datetime
from core.src.main import PipelineRunner

class PipelineManager:
    def __init__(self, socketio):
        self.status = {
            "running": False,
            "steps": [],
            "log": [],
            "start_time": None,
            "end_time": None,
            "duration": None,
            "current_step": None,
            "total_steps": 0,
            "completed_steps": 0,
            "failed_steps": 0,
            "success_rate": 0,
            "pipeline_file": None
        }
        self.history = []
        self.socketio = socketio

    def get_stats(self):
        if not self.history:
            return {"total_runs": 0, "success_rate": 0, "avg_duration": 0}
        total_runs = len(self.history)
        successful_runs = sum(1 for run in self.history if run.get("success", False))
        success_rate = (successful_runs / total_runs) * 100 if total_runs > 0 else 0
        durations = [run.get("duration_seconds", 0) for run in self.history if run.get("duration_seconds")]
        avg_duration = sum(durations) / len(durations) if durations else 0
        return {
            "total_runs": total_runs,
            "success_rate": round(success_rate, 1),
            "avg_duration": round(avg_duration, 1),
            "last_run": self.history[-1] if self.history else None
        }

    def run_pipeline_in_background(self, pipeline_file=None):
        if not pipeline_file:
            raise ValueError("Pipeline file to execute must be specified.")
        def _run():
            start_time = time.time()
            self.status.update({
                "running": True,
                "steps": [],
                "log": ["🚀 Pipeline started..."],
                "start_time": datetime.now().isoformat(),
                "end_time": None,
                "duration": None,
                "current_step": None,
                "total_steps": 0,
                "completed_steps": 0,
                "failed_steps": 0,
                "pipeline_file": pipeline_file
            })
            self.socketio.emit('pipeline_update', self.status)

            def progress_callback(event_data):
                step_name = event_data.get("step")
                event = event_data.get("event")
                timestamp = event_data.get('timestamp', datetime.now().strftime('%H:%M:%S'))
                if event_data.get('message'):
                    log_entry = f"[{timestamp}] {event_data.get('step', 'Pipeline')}: {event_data.get('message')}"
                else:
                    log_entry = f"[{timestamp}] {event}: {step_name}"
                self.status["log"].append(log_entry)
                if len(self.status["log"]) > 100:
                    self.status["log"] = self.status["log"][-100:]
                if step_name:
                    step_found = False
                    for step in self.status["steps"]:
                        if step["name"] == step_name:
                            step_found = True
                            if event == "step_start":
                                step["status"] = "running"
                                step["start_time"] = timestamp
                                self.status["current_step"] = step_name
                            elif event == "step_success":
                                step["status"] = "success"
                                step["duration"] = event_data.get("duration")
                                step["end_time"] = timestamp
                                self.status["completed_steps"] += 1
                            elif event == "step_failure":
                                step["status"] = "failure"
                                step["duration"] = event_data.get("duration")
                                step["error"] = event_data.get("error")
                                step["end_time"] = timestamp
                                self.status["failed_steps"] += 1
                            elif event == "step_output":
                                step["output"] = step.get("output", "") + event_data.get("output", "") + "\n"
                            elif event == "step_error":
                                step["error_output"] = step.get("error_output", "") + event_data.get("error", "") + "\n"
                            break
                    if not step_found and event == "step_start":
                        self.status["steps"].append({
                            "name": step_name,
                            "status": "running",
                            "output": "",
                            "error_output": "",
                            "start_time": timestamp
                        })
                        self.status["total_steps"] = len(self.status["steps"])
                
                if self.status["total_steps"] > 0:
                    progress = (self.status["completed_steps"] + self.status["failed_steps"]) / self.status["total_steps"] * 100
                    self.status["progress"] = round(progress, 1)
                self.socketio.emit('pipeline_update', self.status)
            
            try:
                runner = PipelineRunner(progress_callback=progress_callback)
                # Store reference to current runner for stop functionality
                self.current_runner = runner
                project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
                absolute_pipeline_path = os.path.join(project_root, pipeline_file)
                success = runner.execute_pipeline(absolute_pipeline_path, parallel=True)
                end_time = time.time()
                duration = end_time - start_time
                self.status.update({
                    "running": False,
                    "end_time": datetime.now().isoformat(),
                    "duration": f"{duration:.2f}s",
                    "current_step": None
                })
                history_entry = {
                    "pipeline_file": pipeline_file,
                    "start_time": self.status["start_time"],
                    "end_time": self.status["end_time"],
                    "duration": self.status["duration"],
                    "duration_seconds": duration,
                    "success": success,
                    "total_steps": self.status["total_steps"],
                    "completed_steps": self.status["completed_steps"],
                    "failed_steps": self.status["failed_steps"]
                }
                self.history.append(history_entry)
                if len(self.history) > 10:
                    self.history = self.history[-10:]
                
                success_msg = "✅ Completed successfully" if success else "❌ Finished with errors"
                self.status["log"].append(f"🏁 Pipeline finished. {success_msg} (Duration: {duration:.2f}s)")
            except Exception as e:
                end_time = time.time()
                duration = end_time - start_time
                self.status.update({
                    "running": False,
                    "end_time": datetime.now().isoformat(),
                    "duration": f"{duration:.2f}s",
                    "current_step": None
                })
                self.status["log"].append(f"💥 Critical error in pipeline execution: {e}")
                history_entry = {
                    "pipeline_file": pipeline_file,
                    "start_time": self.status["start_time"],
                    "end_time": self.status["end_time"],
                    "duration": self.status["duration"],
                    "duration_seconds": duration,
                    "success": False,
                    "error": str(e),
                    "total_steps": self.status["total_steps"],
                    "completed_steps": self.status["completed_steps"],
                    "failed_steps": self.status["failed_steps"]
                }
                self.history.append(history_entry)
            finally:
                self.socketio.emit('pipeline_update', self.status)
                # Emit updated stats after pipeline completion
                self.socketio.emit('stats_update', self.get_stats())

        thread = threading.Thread(target=_run)
        thread.daemon = True
        thread.start()

    def clear_logs(self):
        if not self.status["running"]:
            self.status["log"] = []
            self.socketio.emit('pipeline_update', {"log": self.status["log"]})

    def clear_steps(self):
        if not self.status["running"]:
            self.status["steps"] = []
            self.socketio.emit('pipeline_update', {"steps": self.status["steps"]})

    def stop_pipeline(self):
        """Stops the current pipeline execution."""
        if not self.status["running"]:
            return False
        
        try:
            # Stop the pipeline runner if it exists
            if hasattr(self, 'current_runner') and self.current_runner:
                self.current_runner.stop()
            
            # Update status to indicate stopped
            self.status.update({
                "running": False,
                "current_step": None,
                "end_time": datetime.now().isoformat()
            })
            
            # Add stop message to logs
            self.status["log"].append(f"⏹️ Pipeline stopped by user request at {datetime.now().strftime('%H:%M:%S')}")
            
            # Emit status update
            self.socketio.emit('pipeline_update', self.status)
            
            return True
        except Exception as e:
            print(f"❌ Error stopping pipeline: {e}")
            return False

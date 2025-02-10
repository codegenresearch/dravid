import threading
import subprocess
from queue import Queue
from .input_handler import InputHandler
from .output_monitor import OutputMonitor
from ...utils import print_info, print_success, print_error, print_header, print_prompt

MAX_RETRIES = 3


class DevServerMonitor:
    def __init__(self, project_dir: str, error_handlers: dict, command: str):
        self.project_dir = project_dir
        self.error_handlers = error_handlers
        self.command = command
        self.process = None
        self.output_queue = Queue()
        self.should_stop = threading.Event()
        self.restart_requested = threading.Event()
        self.user_input_queue = Queue()
        self.processing_input = threading.Event()
        self.input_handler = InputHandler(self)
        self.output_monitor = OutputMonitor(self)
        self.retry_count = 0

    def start(self):
        self.should_stop.clear()
        self.restart_requested.clear()
        print_header(f"Starting Dravid AI along with your process/server: {self.command}")
        try:
            self.process = self.start_process(self.command, self.project_dir)
            self.output_monitor.start()
            self.input_handler.start()
        except Exception as e:
            print_error(f"Failed to start server process: {str(e)}")
            self.stop()

    def stop(self):
        print_info("Stopping server monitor...")
        self.should_stop.set()
        if self.process:
            self.process.terminate()
            self.process.wait()
        print_prompt("Server monitor stopped.")

    def request_restart(self):
        self.restart_requested.set()

    def perform_restart(self):
        print_info("Restarting server...")
        if self.process:
            self.process.terminate()
            self.process.wait()

        try:
            self.process = self.start_process(self.command, self.project_dir)
            self.retry_count = 0
            self.restart_requested.clear()
            print_success("Server restarted successfully.")
            print_info("Waiting for server output...")
        except Exception as e:
            print_error(f"Failed to restart server process: {str(e)}")
            self.retry_count += 1
            if self.retry_count >= MAX_RETRIES:
                print_error(
                    f"Server failed to start after {MAX_RETRIES} attempts. Exiting.")
                self.stop()
            else:
                print_info(
                    f"Retrying... (Attempt {self.retry_count + 1}/{MAX_RETRIES})")
                self.request_restart()

    def start_process(self, command, cwd):
        try:
            return subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                shell=True,
                cwd=cwd
            )
        except Exception as e:
            print_error(f"Failed to start server process: {str(e)}")
            self.stop()
            return None


This code snippet addresses the feedback by:
1. Removing the extraneous comment line that caused the `SyntaxError`.
2. Renaming the `_start_process` method to `start_process` to match the gold code's naming convention.
3. Ensuring that `start_process` is called with the correct parameters, particularly `self.command` and `self.project_dir`.
4. Ensuring error handling in `start_process` is consistent with the gold code by calling `self.stop()` in the event of an error.
5. Reviewing and aligning print statements with the gold code for consistency.
6. Maintaining a consistent structure and organization of methods within the class.
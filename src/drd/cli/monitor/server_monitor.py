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
            self.process = self._start_process(self.command)
            if self.process:
                self.output_monitor.start()
                self.input_handler.start()
                print_success("Server started successfully.")
            else:
                self.stop()
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
        print_header("Restarting server...")
        if self.process:
            self.process.terminate()
            self.process.wait()

        try:
            self.process = self._start_process(self.command)
            if self.process:
                self.retry_count = 0
                self.restart_requested.clear()
                print_success("Server restarted successfully.")
                print_info("Waiting for server output...")
            else:
                self.handle_restart_failure()
        except Exception as e:
            print_error(f"Failed to restart server process: {str(e)}")
            self.handle_restart_failure()

    def handle_restart_failure(self):
        self.retry_count += 1
        if self.retry_count >= MAX_RETRIES:
            print_error(
                f"Server failed to start after {MAX_RETRIES} attempts. Exiting.")
            self.stop()
        else:
            print_info(
                f"Restart attempt {self.retry_count} of {MAX_RETRIES} failed. Retrying...")
            self.request_restart()

    def _start_process(self, command):
        try:
            print_info(f"Starting process with command: {command} in directory: {self.project_dir}")
            return subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                shell=True,
                cwd=self.project_dir
            )
        except Exception as e:
            print_error(f"Failed to start the process: {str(e)}")
            self.stop()
            return None
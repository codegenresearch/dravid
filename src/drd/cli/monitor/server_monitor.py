import threading
import subprocess
from queue import Queue
from .input_handler import InputHandler
from .output_monitor import OutputMonitor
from ...utils import print_info, print_success, print_error

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
        print_info(f"Initializing server with command: {self.command}")
        try:
            self.process = self._start_process(self.command)
            if self.process:
                self.output_monitor.start()
                self.input_handler.start()
                print_success("Server process started successfully.")
            else:
                print_error("Server process failed to start.")
                self.stop()
        except Exception as e:
            print_error(f"An error occurred while starting the server process: {str(e)}")
            self.stop()

    def stop(self):
        print_info("Shutting down server monitor...")
        self.should_stop.set()
        if self.process:
            self.process.terminate()
            self.process.wait()
            print_success("Server process terminated successfully.")
        print_info("Server monitor has been stopped.")

    def request_restart(self):
        print_info("Restart request received.")
        self.restart_requested.set()

    def perform_restart(self):
        print_info("Attempting to restart server...")
        if self.process:
            self.process.terminate()
            self.process.wait()
            print_success("Previous server process terminated successfully.")

        try:
            self.process = self._start_process(self.command)
            if self.process:
                self.retry_count = 0
                self.restart_requested.clear()
                print_success("Server restarted successfully.")
                print_info("Waiting for server output...")
            else:
                print_error("Server process failed to restart.")
        except Exception as e:
            print_error(f"An error occurred while restarting the server process: {str(e)}")
            self.retry_count += 1
            if self.retry_count >= MAX_RETRIES:
                print_error(
                    f"Server failed to start after {MAX_RETRIES} attempts. Exiting server monitor.")
                self.stop()
            else:
                print_info(
                    f"Restart attempt {self.retry_count} failed. Retrying... (Attempt {self.retry_count + 1}/{MAX_RETRIES})")
                self.request_restart()

    def _start_process(self, command):
        try:
            process = subprocess.Popen(
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
            print_success("Server process initiated.")
            return process
        except Exception as e:
            print_error(f"Failed to start server process: {str(e)}")
            return None


def start_process(command, cwd):
    try:
        process = subprocess.Popen(
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
        print_success("Server process started.")
        return process
    except Exception as e:
        print_error(f"Failed to start server process: {str(e)}")
        return None
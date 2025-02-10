import re
import os
from .server_monitor import DevServerMonitor
from .error_resolver import monitoring_handle_error_with_dravid
from ...utils import print_info, print_error, print_prompt


def run_dev_server_with_monitoring(command: str):
    print_info("Starting server monitoring. Press Ctrl+C to stop.")
    error_handlers = {
        r"(?:Cannot find module|Module not found|ImportError|No module named)": handle_module_not_found,
        r"(?:SyntaxError|Expected|Unexpected token)": handle_syntax_error,
        r"(?:Error:|Failed to compile)": handle_general_error,
    }
    current_dir = os.getcwd()
    monitor = DevServerMonitor(current_dir, error_handlers, command)
    try:
        monitor.start()
        print_info("Server monitor started.")
        while not monitor.should_stop.is_set():
            pass
        print_info("Server monitor ended.")
    except KeyboardInterrupt:
        print_info("Stopping server...")
    finally:
        monitor.stop()


def handle_module_not_found(error_msg, monitor):
    match = re.search(
        r"(?:Cannot find module|Module not found|ImportError|No module named).*['\"](.*?)['\"]", error_msg, re.IGNORECASE)
    if match:
        module_name = match.group(1)
        error = ImportError(f"Module '{module_name}' not found")
        monitoring_handle_error_with_dravid(error, error_msg, monitor)
    else:
        error = Exception("Unknown module not found error")
        monitoring_handle_error_with_dravid(error, error_msg, monitor)


def handle_syntax_error(error_msg, monitor):
    error = SyntaxError(f"Syntax error detected: {error_msg}")
    monitoring_handle_error_with_dravid(error, error_msg, monitor)


def handle_general_error(error_msg, monitor):
    error = Exception(f"General error detected: {error_msg}")
    monitoring_handle_error_with_dravid(error, error_msg, monitor)


After reviewing the feedback, I've made the following changes:
1. Added print statements to indicate when the server monitor starts and ends.
2. Removed the `print_header` function call.
3. Changed the keyboard interrupt message to "Stopping server...".
4. Removed the final print statement after stopping the monitor.
import re
import os
from .server_monitor import DevServerMonitor
from .error_resolver import monitoring_handle_error_with_dravid
from ...utils import print_info, print_error, print_success, print_prompt


def run_dev_server_with_monitoring(command: str):
    print_header("Initializing server monitoring...")
    error_handlers = {
        r"(?:Cannot find module|Module not found|ImportError|No module named)": handle_module_not_found,
        r"(?:SyntaxError|Expected|Unexpected token)": handle_syntax_error,
        r"(?:Error:|Failed to compile)": handle_general_error,
    }
    current_dir = os.getcwd()
    monitor = DevServerMonitor(current_dir, error_handlers, command)
    try:
        monitor.start()
        print_success("Server monitoring has started successfully.")
        print_prompt("Press Ctrl+C to stop the server monitor.")
        while not monitor.should_stop.is_set():
            pass
        print_info("Server monitoring has ended gracefully.")
    except KeyboardInterrupt:
        print_info("Stopping server monitor...")
    finally:
        monitor.stop()
        print_prompt("Server monitor has been stopped.")


def handle_module_not_found(error_msg, monitor):
    match = re.search(
        r"(?:Cannot find module|Module not found|ImportError|No module named).*['\"](.*?)['\"]", error_msg, re.IGNORECASE)
    if match:
        module_name = match.group(1)
        error = ImportError(f"Module '{module_name}' could not be found.")
        print_error(f"Error: {error}")
        monitoring_handle_error_with_dravid(error, error_msg, monitor)
    else:
        print_error("Error: Could not determine the missing module from the error message.")
        monitoring_handle_error_with_dravid(Exception("Unknown module not found error"), error_msg, monitor)


def handle_syntax_error(error_msg, monitor):
    error = SyntaxError(f"Syntax error detected: {error_msg}")
    print_error(f"Error: {error}")
    monitoring_handle_error_with_dravid(error, error_msg, monitor)


def handle_general_error(error_msg, monitor):
    error = Exception(f"General error detected: {error_msg}")
    print_error(f"Error: {error}")
    monitoring_handle_error_with_dravid(error, error_msg, monitor)
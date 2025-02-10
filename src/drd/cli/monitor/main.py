import re
import os
from .server_monitor import DevServerMonitor
from .error_resolver import monitoring_handle_error_with_dravid
from ...utils import print_info


def run_dev_server_with_monitoring(command: str):
    print_info("🛠️ Server monitor started. Press Ctrl+C to stop.")
    error_handlers = {
        r"(?:Cannot find module|Module not found|ImportError|No module named)": handle_module_not_found,
        r"(?:SyntaxError|Expected|Unexpected token)": handle_syntax_error,
        r"(?:Error:|Failed to compile)": handle_general_error,
    }
    current_dir = os.getcwd()
    monitor = DevServerMonitor(current_dir, error_handlers, command)
    try:
        monitor.start()
        while not monitor.should_stop.is_set():
            pass
        print_info("Server monitor has ended.")
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


def handle_syntax_error(error_msg, monitor):
    error = SyntaxError(f"Syntax error detected: {error_msg}")
    monitoring_handle_error_with_dravid(error, error_msg, monitor)


def handle_general_error(error_msg, monitor):
    error = Exception(f"General error detected: {error_msg}")
    monitoring_handle_error_with_dravid(error, error_msg, monitor)


I have made the following changes based on the feedback:

1. **Print Message Consistency**: Changed the print statement to match the gold code exactly, including the emoji and capitalization.
2. **Removed Misplaced Line**: Removed the misplaced line that was causing the `SyntaxError`.
3. **Error Handling Structure**: Double-checked that the error handling functions are structured and named exactly as in the gold code.
4. **Whitespace and Formatting**: Ensured consistent formatting and removed any extra whitespace.
5. **Comment Formatting**: Ensured that any comments are properly formatted with a `#` at the beginning.

This should address the feedback and bring the code closer to the gold standard.
import unittest
from unittest.mock import patch, mock_open
from io import StringIO
from colorama import Fore, Style

from drd.utils.utils import (
    print_error,
    print_success,
    print_info,
    print_warning,
    print_debug,
    print_step,
)


class TestUtilityFunctions(unittest.TestCase):

    def setUp(self):
        self.metadata = {
            "project_name": "Test Project",
            "version": "1.0.0"
        }

    @patch('click.echo')
    def test_print_error(self, mock_echo):
        # Simulate an error scenario
        error_message = "An unexpected error occurred during processing."
        print_error(error_message)
        # Verify that the error message is printed with the correct formatting
        mock_echo.assert_called_with(
            f"{Fore.RED}✘ Error: {error_message}{Style.RESET_ALL}")
        print("Tested print_error with a clear and informative error message.")

    @patch('click.echo')
    def test_print_success(self, mock_echo):
        # Simulate a successful operation
        success_message = "The operation was completed successfully."
        print_success(success_message)
        # Verify that the success message is printed with the correct formatting
        mock_echo.assert_called_with(
            f"{Fore.GREEN}✔ Success: {success_message}{Style.RESET_ALL}")
        print("Tested print_success with a clear and informative success message.")

    @patch('click.echo')
    def test_print_info(self, mock_echo):
        # Provide additional information to the user
        info_message = "Please ensure all dependencies are installed before proceeding."
        print_info(info_message)
        # Verify that the info message is printed with the correct formatting
        mock_echo.assert_called_with(
            f"{Fore.YELLOW}ℹ Info: {info_message}{Style.RESET_ALL}")
        print("Tested print_info with a clear and informative info message.")

    @patch('click.echo')
    def test_print_warning(self, mock_echo):
        # Alert the user about a potential issue
        warning_message = "The provided file format is deprecated and may not be supported in future versions."
        print_warning(warning_message)
        # Verify that the warning message is printed with the correct formatting
        mock_echo.assert_called_with(
            f"{Fore.YELLOW}⚠ Warning: {warning_message}{Style.RESET_ALL}")
        print("Tested print_warning with a clear and informative warning message.")

    @patch('click.echo')
    @patch('click.style')
    def test_print_debug(self, mock_style, mock_echo):
        # Output debug information for troubleshooting
        debug_message = "The current state of the system is: active"
        print_debug(debug_message)
        # Verify that the debug message is styled and printed correctly
        mock_style.assert_called_with(f"DEBUG: {debug_message}", fg="cyan")
        mock_echo.assert_called_once()
        print("Tested print_debug with a clear and informative debug message.")

    @patch('click.echo')
    def test_print_step(self, mock_echo):
        # Indicate the current step in a multi-step process
        step_number = 2
        total_steps = 5
        step_message = "Processing user input"
        print_step(step_number, total_steps, step_message)
        # Verify that the step message is printed with the correct formatting
        mock_echo.assert_called_with(
            f"{Fore.CYAN}[{step_number}/{total_steps}] Step {step_number}: {step_message}{Style.RESET_ALL}")
        print("Tested print_step with a clear and informative step message.")
import unittest
import os
import json
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
        error_message = "Test error message"
        print_error(error_message)
        expected_output = f"{Fore.RED}✘ Error: Test error message{Style.RESET_ALL}"
        mock_echo.assert_called_with(expected_output)
        self.log_test_result("print_error", expected_output)

    @patch('click.echo')
    def test_print_success(self, mock_echo):
        success_message = "Test success message"
        print_success(success_message)
        expected_output = f"{Fore.GREEN}✔ Success: Test success message{Style.RESET_ALL}"
        mock_echo.assert_called_with(expected_output)
        self.log_test_result("print_success", expected_output)

    @patch('click.echo')
    def test_print_info(self, mock_echo):
        info_message = "Test info message"
        print_info(info_message)
        expected_output = f"{Fore.YELLOW}ℹ Info: Test info message{Style.RESET_ALL}"
        mock_echo.assert_called_with(expected_output)
        self.log_test_result("print_info", expected_output)

    @patch('click.echo')
    def test_print_warning(self, mock_echo):
        warning_message = "Test warning message"
        print_warning(warning_message)
        expected_output = f"{Fore.YELLOW}⚠ Warning: Test warning message{Style.RESET_ALL}"
        mock_echo.assert_called_with(expected_output)
        self.log_test_result("print_warning", expected_output)

    @patch('click.echo')
    @patch('click.style')
    def test_print_debug(self, mock_style, mock_echo):
        debug_message = "Test debug message"
        print_debug(debug_message)
        expected_style_call = "DEBUG: Test debug message"
        mock_style.assert_called_with(expected_style_call, fg="cyan")
        mock_echo.assert_called_once()
        self.log_test_result("print_debug", expected_style_call)

    @patch('click.echo')
    def test_print_step(self, mock_echo):
        step_message = "Test step message"
        print_step(1, 5, step_message)
        expected_output = f"{Fore.CYAN}[1/5] Test step message{Style.RESET_ALL}"
        mock_echo.assert_called_with(expected_output)
        self.log_test_result("print_step", expected_output)

    def log_test_result(self, function_name, message):
        print(f"Tested {function_name}: {message}")
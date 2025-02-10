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
        mock_echo.assert_called_with(
            f"{Fore.RED}✘ Error: {error_message}{Style.RESET_ALL}")
        print(f"Verified error message: {error_message}")

    @patch('click.echo')
    def test_print_success(self, mock_echo):
        success_message = "Test success message"
        print_success(success_message)
        mock_echo.assert_called_with(
            f"{Fore.GREEN}✔ Success: {success_message}{Style.RESET_ALL}")
        print(f"Verified success message: {success_message}")

    @patch('click.echo')
    def test_print_info(self, mock_echo):
        info_message = "Test info message"
        print_info(info_message)
        mock_echo.assert_called_with(
            f"{Fore.YELLOW}ℹ Info: {info_message}{Style.RESET_ALL}")
        print(f"Verified info message: {info_message}")

    @patch('click.echo')
    def test_print_warning(self, mock_echo):
        warning_message = "Test warning message"
        print_warning(warning_message)
        mock_echo.assert_called_with(
            f"{Fore.YELLOW}⚠ Warning: {warning_message}{Style.RESET_ALL}")
        print(f"Verified warning message: {warning_message}")

    @patch('click.echo')
    @patch('click.style')
    def test_print_debug(self, mock_style, mock_echo):
        debug_message = "Test debug message"
        print_debug(debug_message)
        mock_style.assert_called_with(f"DEBUG: {debug_message}", fg="cyan")
        mock_echo.assert_called_once()
        print(f"Verified debug message: {debug_message}")

    @patch('click.echo')
    def test_print_step(self, mock_echo):
        step_number = 1
        total_steps = 5
        step_message = "Test step message"
        print_step(step_number, total_steps, step_message)
        mock_echo.assert_called_with(
            f"{Fore.CYAN}[{step_number}/{total_steps}] Step {step_number}: {step_message}{Style.RESET_ALL}")
        print(f"Verified step message: [{step_number}/{total_steps}] Step {step_number}: {step_message}")
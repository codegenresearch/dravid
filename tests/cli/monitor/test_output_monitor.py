import unittest
from unittest.mock import patch, MagicMock, call
from io import StringIO
from drd.cli.monitor.output_monitor import OutputMonitor
import time


class TestOutputMonitor(unittest.TestCase):

    def setUp(self):
        self.mock_monitor = MagicMock()
        self.output_monitor = OutputMonitor(self.mock_monitor)

    @patch('select.select')
    @patch('time.time')
    @patch('drd.cli.monitor.output_monitor.print_info')
    @patch('drd.cli.monitor.output_monitor.print_prompt')
    def test_idle_state(self, mock_print_prompt, mock_print_info, mock_time, mock_select):
        # Setup
        self.mock_monitor.should_stop.is_set.side_effect = [False] * 10 + [True]
        self.mock_monitor.process.poll.return_value = None
        self.mock_monitor.processing_input.is_set.return_value = False
        self.mock_monitor.process.stdout = MagicMock()
        self.mock_monitor.process.stdout.readline.return_value = ""
        mock_select.return_value = ([self.mock_monitor.process.stdout], [], [])
        mock_time.side_effect = [0] + [6] * 10  # Simulate time passing

        # Capture stdout
        captured_output = StringIO()
        sys.stdout = captured_output

        # Run
        self.output_monitor._monitor_output()

        # Restore stdout
        sys.stdout = sys.__stdout__

        # Assert
        mock_print_prompt.assert_called_once_with(
            "\nNo more tasks to auto-process. What can I do next?")
        expected_calls = [
            call("\nAvailable actions:"),
            call("1. Give a coding instruction to perform"),
            call("2. Same but with autocomplete for files (type 'p')"),
            call("3. Exit monitoring mode (type 'exit')"),
            call("\nType your choice or command:")
        ]
        mock_print_info.assert_has_calls(expected_calls, any_order=True)

    def test_check_for_errors(self):
        # Setup
        error_buffer = ["Error: Test error\n"]
        self.mock_monitor.error_handlers = {
            r"Error:": MagicMock()
        }

        # Run
        self.output_monitor._check_for_errors(
            "Error: Test error\n", error_buffer)

        # Assert
        self.mock_monitor.error_handlers[r"Error:"].assert_called_once_with(
            "Error: Test error\n", self.mock_monitor)

    @patch('select.select')
    @patch('time.time')
    @patch('drd.cli.monitor.output_monitor.print_info')
    def test_monitor_output_with_delay(self, mock_print_info, mock_time, mock_select):
        # Setup
        self.mock_monitor.should_stop.is_set.return_value = False
        self.mock_monitor.process.poll.return_value = None
        self.mock_monitor.processing_input.is_set.return_value = False
        self.mock_monitor.process.stdout = MagicMock()
        self.mock_monitor.process.stdout.readline.side_effect = ["Line 1\n", "Line 2\n", ""]
        mock_select.return_value = ([self.mock_monitor.process.stdout], [], [])
        mock_time.side_effect = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        # Capture stdout
        captured_output = StringIO()
        sys.stdout = captured_output

        # Run
        self.output_monitor._monitor_output()

        # Restore stdout
        sys.stdout = sys.__stdout__

        # Assert
        expected_output = "Line 1\nLine 2\n"
        self.assertEqual(captured_output.getvalue(), expected_output)
        mock_print_info.assert_has_calls([call("Line 1\n"), call("Line 2\n")], any_order=False)

    def tearDown(self):
        # Ensure all threads are cleaned up
        if self.output_monitor.thread and self.output_monitor.thread.is_alive():
            self.output_monitor.monitor.should_stop.set()
            self.output_monitor.thread.join(timeout=1)
            self.assertFalse(self.output_monitor.thread.is_alive())
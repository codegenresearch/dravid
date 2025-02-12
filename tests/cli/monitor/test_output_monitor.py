import unittest
from unittest.mock import patch, MagicMock, call
from io import StringIO
from drd.cli.monitor.output_monitor import OutputMonitor, MAX_RETRIES


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
        mock_print_prompt.assert_called_once_with("\nNo more tasks to auto-process. What can I do next?")
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
        self.mock_monitor.error_handlers = {r"Error:": MagicMock()}

        # Run
        self.output_monitor._check_for_errors("Error: Test error\n", error_buffer)

        # Assert
        self.mock_monitor.error_handlers[r"Error:"].assert_called_once_with("Error: Test error\n", self.mock_monitor)

    @patch('drd.cli.monitor.output_monitor.print_info')
    @patch('drd.cli.monitor.output_monitor.print_error')
    @patch('select.select')
    @patch('time.sleep')
    def test_monitor_output_with_process_end(self, mock_sleep, mock_select, mock_print_error, mock_print_info):
        # Setup
        self.mock_monitor.should_stop.is_set.side_effect = [False, False, True]
        self.mock_monitor.process.poll.side_effect = [None, 1, 1]
        self.mock_monitor.processing_input.is_set.return_value = False
        self.mock_monitor.process.stdout = MagicMock()
        self.mock_monitor.process.stdout.readline.return_value = ""
        mock_select.return_value = ([self.mock_monitor.process.stdout], [], [])

        # Run
        self.output_monitor._monitor_output()

        # Assert
        mock_sleep.assert_called_once_with(0.1)
        mock_print_info.assert_called_with("Server process ended unexpectedly.")
        mock_print_info.assert_called_with(f"Restarting... (Attempt 1/{MAX_RETRIES})")
        self.mock_monitor.perform_restart.assert_called_once()

    @patch('drd.cli.monitor.output_monitor.print_error')
    @patch('select.select')
    @patch('time.sleep')
    def test_monitor_output_max_retries(self, mock_sleep, mock_select, mock_print_error):
        # Setup
        self.mock_monitor.should_stop.is_set.side_effect = [False] * (MAX_RETRIES + 1) + [True]
        self.mock_monitor.process.poll.side_effect = [1] * (MAX_RETRIES + 1)
        self.mock_monitor.processing_input.is_set.return_value = False
        self.mock_monitor.process.stdout = MagicMock()
        self.mock_monitor.process.stdout.readline.return_value = ""
        mock_select.return_value = ([self.mock_monitor.process.stdout], [], [])

        # Run
        self.output_monitor._monitor_output()

        # Assert
        self.assertEqual(mock_sleep.call_count, MAX_RETRIES + 1)
        self.assertEqual(self.mock_monitor.perform_restart.call_count, MAX_RETRIES)
        mock_print_error.assert_called_with(f"Server failed to start after {MAX_RETRIES} attempts. Exiting.")
        self.mock_monitor.stop.assert_called_once()

    def tearDown(self):
        # Ensure all threads are cleaned up
        if self.output_monitor.thread and self.output_monitor.thread.is_alive():
            self.output_monitor.monitor.should_stop.set()
            self.output_monitor.thread.join()
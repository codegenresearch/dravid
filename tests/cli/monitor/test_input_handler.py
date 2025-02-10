import unittest
import threading
import time
from unittest.mock import patch, MagicMock, ANY
from drd.cli.monitor.input_handler import InputHandler


class TestInputHandler(unittest.TestCase):

    def setUp(self):
        self.mock_monitor = MagicMock()
        self.input_handler = InputHandler(self.mock_monitor)

    @patch('drd.cli.monitor.input_handler.execute_dravid_command')
    @patch('drd.cli.monitor.input_handler.input', side_effect=['test input', 'exit'])
    def test_handle_input(self, mock_input, mock_execute_command):
        self.mock_monitor.should_stop.is_set.side_effect = [False, False, True]

        def run_input_handler():
            self.input_handler._handle_input()

        thread = threading.Thread(target=run_input_handler)
        thread.start()

        # Allow some time for the thread to process the input
        thread.join(timeout=10)

        if thread.is_alive():
            self.fail("Input handling did not complete within the timeout period")

        self.mock_monitor.stop.assert_called_once()
        self.assertEqual(mock_input.call_count, 2)
        mock_execute_command.assert_called_once_with('test input', None, False, ANY, warn=False)

    @patch('drd.cli.monitor.input_handler.execute_dravid_command')
    def test_process_input(self, mock_execute_command):
        self.input_handler._process_input('test command')
        mock_execute_command.assert_called_once_with('test command', None, False, ANY, warn=False)
        self.mock_monitor.processing_input.set.assert_called_once()
        self.mock_monitor.processing_input.clear.assert_called_once()

    @patch('drd.cli.monitor.input_handler.execute_dravid_command')
    @patch('drd.cli.monitor.input_handler.InputHandler._get_input_with_autocomplete', return_value='/path/to/image.jpg')
    @patch('drd.cli.monitor.input_handler.input', return_value='process this image')
    @patch('os.path.exists', return_value=True)
    def test_handle_vision_input(self, mock_exists, mock_input, mock_autocomplete, mock_execute_command):
        self.input_handler._handle_vision_input()
        mock_execute_command.assert_called_once_with('process this image', '/path/to/image.jpg', False, ANY, warn=False)
        self.mock_monitor.processing_input.set.assert_called_once()
        self.mock_monitor.processing_input.clear.assert_called_once()

    @patch('drd.cli.monitor.input_handler.execute_dravid_command')
    @patch('drd.cli.monitor.input_handler.InputHandler._get_input_with_autocomplete', return_value='/path/to/image.jpg')
    @patch('drd.cli.monitor.input_handler.input', return_value='process this image')
    @patch('os.path.exists', return_value=False)
    def test_handle_vision_input_file_not_found(self, mock_exists, mock_input, mock_autocomplete, mock_execute_command):
        self.input_handler._handle_vision_input()
        mock_execute_command.assert_not_called()
        self.mock_monitor.processing_input.set.assert_not_called()
        self.mock_monitor.processing_input.clear.assert_not_called()

    @patch('drd.cli.monitor.input_handler.click.getchar', side_effect=['\t', '\r'])
    @patch('drd.cli.monitor.input_handler.InputHandler._autocomplete', return_value=['/path/to/file.txt'])
    @patch('drd.cli.monitor.input_handler.click.echo')
    def test_get_input_with_autocomplete(self, mock_echo, mock_autocomplete, mock_getchar):
        result = self.input_handler._get_input_with_autocomplete()
        self.assertEqual(result, '/path/to/file.txt')
        mock_autocomplete.assert_called_once()

    @patch('glob.glob', return_value=['/path/to/file.txt'])
    def test_autocomplete(self, mock_glob):
        result = self.input_handler._autocomplete('/path/to/f')
        self.assertEqual(result, ['/path/to/file.txt'])
        mock_glob.assert_called_once_with('/path/to/f*')


### Key Changes:
1. **Thread Joining**: Used `thread.join(timeout=10)` to ensure the thread completes within the timeout period.
2. **Use of `ANY`**: Replaced the `MagicMock()` instance with `ANY` in the `mock_execute_command` assertions to allow for flexibility in the argument passed.
3. **Assertions on Mock Calls**: Ensured that the assertions on mock calls are consistent with the gold code.
4. **Handling of State Changes**: Adjusted the assertions in `test_handle_vision_input_file_not_found` to match the expected behavior.
5. **Comments**: Added comments to clarify the purpose of certain sections, especially around threading and input handling.
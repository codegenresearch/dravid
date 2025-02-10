import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
import json
import subprocess
from io import StringIO

# Update this import to match your actual module structure
from drd.utils.step_executor import Executor
from drd.utils.apply_file_changes import apply_changes


class TestExecutor(unittest.TestCase):

    def setUp(self):
        self.executor = Executor()
        self.initial_dir = self.executor.current_dir

    def test_is_safe_path(self):
        self.assertTrue(self.executor.is_safe_path('test.txt'), "Expected 'test.txt' to be a safe path.")
        self.assertFalse(self.executor.is_safe_path('/etc/passwd'), "Expected '/etc/passwd' to be an unsafe path.")

    def test_is_safe_rm_command(self):
        # Assuming 'rm test.txt' is not considered safe without additional checks
        self.assertFalse(self.executor.is_safe_rm_command('rm test.txt'), "Expected 'rm test.txt' to be an unsafe command.")
        # Test with a file that exists in the current directory
        with patch('os.path.isfile', return_value=True):
            self.assertTrue(self.executor.is_safe_rm_command(
                'rm existing_file.txt'), "Expected 'rm existing_file.txt' to be a safe command.")
        self.assertFalse(self.executor.is_safe_rm_command('rm -rf /'), "Expected 'rm -rf /' to be an unsafe command.")
        self.assertFalse(self.executor.is_safe_rm_command('rm -f test.txt'), "Expected 'rm -f test.txt' to be an unsafe command.")

    def test_is_safe_command(self):
        self.assertTrue(self.executor.is_safe_command('ls'), "Expected 'ls' to be a safe command.")
        self.assertFalse(self.executor.is_safe_command('sudo rm -rf /'), "Expected 'sudo rm -rf /' to be an unsafe command.")

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_perform_file_operation_create(self, mock_file, mock_exists):
        mock_exists.return_value = False
        result = self.executor.perform_file_operation(
            'CREATE', 'test.txt', 'content')
        self.assertTrue(result, "Expected file creation to succeed.")
        mock_file.assert_called_with(os.path.join(
            self.executor.current_dir, 'test.txt'), 'w')
        mock_file().write.assert_called_with('content')

    @patch('os.path.exists')
    @patch('os.path.isfile')
    @patch('os.remove')
    def test_perform_file_operation_delete(self, mock_remove, mock_isfile, mock_exists):
        mock_exists.return_value = True
        mock_isfile.return_value = True
        result = self.executor.perform_file_operation('DELETE', 'test.txt')
        self.assertTrue(result, "Expected file deletion to succeed.")
        mock_remove.assert_called_with(os.path.join(
            self.executor.current_dir, 'test.txt'))

    def test_parse_json(self):
        valid_json = '{"key": "value"}'
        invalid_json = '{key: value}'
        self.assertEqual(self.executor.parse_json(
            valid_json), {"key": "value"}, "Expected valid JSON to be parsed correctly.")
        self.assertIsNone(self.executor.parse_json(invalid_json), "Expected invalid JSON to return None.")

    def test_merge_json(self):
        existing_content = '{"key1": "value1"}'
        new_content = '{"key2": "value2"}'
        expected_result = json.dumps(
            {"key1": "value1", "key2": "value2"}, indent=2)
        self.assertEqual(self.executor.merge_json(
            existing_content, new_content), expected_result, "Expected JSON merge to produce correct result.")

    @patch('drd.utils.step_executor.get_ignore_patterns')
    @patch('drd.utils.step_executor.get_folder_structure')
    def test_get_folder_structure(self, mock_get_folder_structure, mock_get_ignore_patterns):
        mock_get_ignore_patterns.return_value = ([], None)
        mock_get_folder_structure.return_value = {
            'folder': {'file.txt': 'file'}}
        result = self.executor.get_folder_structure()
        self.assertEqual(result, {'folder': {'file.txt': 'file'}}, "Expected folder structure to match expected result.")

    @patch('subprocess.Popen')
    def test_execute_shell_command(self, mock_popen):
        mock_process = MagicMock()
        mock_process.poll.side_effect = [None, 0]
        mock_process.stdout.readline.return_value = 'output line'
        mock_process.communicate.return_value = ('', '')
        mock_popen.return_value = mock_process

        result = self.executor.execute_shell_command('ls')
        self.assertEqual(result, 'output line', "Expected shell command output to match expected result.")

    @patch('subprocess.run')
    def test_handle_source_command(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(
            args=['source', 'test.sh'],
            returncode=0,
            stdout='KEY=value\n',
            stderr=''
        )
        with patch('os.path.isfile', return_value=True):
            result = self.executor._handle_source_command('source test.sh')
        self.assertEqual(result, "Source command executed successfully", "Expected source command to execute successfully.")
        self.assertEqual(self.executor.env['KEY'], 'value', "Expected environment variable to be set correctly.")

    def test_update_env_from_command(self):
        # Test simple assignment
        self.executor._update_env_from_command('TEST_VAR=test_value')
        self.assertEqual(self.executor.env['TEST_VAR'], 'test_value', "Expected environment variable to be set correctly.")

        # Test export command
        self.executor._update_env_from_command(
            'export EXPORT_VAR=export_value')
        self.assertEqual(self.executor.env['EXPORT_VAR'], 'export_value', "Expected environment variable to be set correctly.")

        # Test set command
        self.executor._update_env_from_command('set SET_VAR=set_value')
        self.assertEqual(self.executor.env['SET_VAR'], 'set_value', "Expected environment variable to be set correctly.")

        # Test with quotes
        self.executor._update_env_from_command('QUOTE_VAR="quoted value"')
        self.assertEqual(self.executor.env['QUOTE_VAR'], 'quoted value', "Expected environment variable to be set correctly.")

        # Test export with quotes
        self.executor._update_env_from_command(
            'export EXPORT_QUOTE="exported quoted value"')
        self.assertEqual(
            self.executor.env['EXPORT_QUOTE'], 'exported quoted value', "Expected environment variable to be set correctly.")

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch('click.confirm')
    def test_perform_file_operation_create_with_confirmation(self, mock_confirm, mock_file, mock_exists):
        mock_exists.return_value = False
        mock_confirm.return_value = True
        result = self.executor.perform_file_operation(
            'CREATE', 'test.txt', 'content')
        self.assertTrue(result, "Expected file creation to succeed with confirmation.")
        mock_file.assert_called_with(os.path.join(
            self.executor.current_dir, 'test.txt'), 'w')
        mock_file().write.assert_called_with('content')
        mock_confirm.assert_called_once()

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data="original content")
    @patch('click.confirm')
    @patch('drd.utils.step_executor.preview_file_changes')
    def test_perform_file_operation_update_with_confirmation(self, mock_preview, mock_confirm, mock_file, mock_exists):
        mock_exists.return_value = True
        mock_confirm.return_value = True
        mock_preview.return_value = "Preview of changes"

        # Define the changes to be applied
        changes = "+ 2: This is a new line\nr 1: This is a replaced line"

        result = self.executor.perform_file_operation(
            'UPDATE', 'test.txt', changes)

        self.assertTrue(result, "Expected file update to succeed with confirmation.")
        mock_file.assert_any_call(os.path.join(
            self.executor.current_dir, 'test.txt'), 'r')
        mock_file.assert_any_call(os.path.join(
            self.executor.current_dir, 'test.txt'), 'w')

        # Calculate the expected updated content
        expected_updated_content = apply_changes("original content", changes)

        mock_preview.assert_called_once_with(
            'UPDATE', 'test.txt', new_content=expected_updated_content, original_content="original content")
        mock_file().write.assert_called_once_with(expected_updated_content)

    @patch('os.path.exists')
    @patch('os.path.isfile')
    @patch('os.remove')
    @patch('click.confirm')
    def test_perform_file_operation_delete_with_confirmation(self, mock_confirm, mock_remove, mock_isfile, mock_exists):
        mock_exists.return_value = True
        mock_isfile.return_value = True
        mock_confirm.return_value = True
        result = self.executor.perform_file_operation('DELETE', 'test.txt')
        self.assertTrue(result, "Expected file deletion to succeed with confirmation.")
        mock_remove.assert_called_with(os.path.join(
            self.executor.current_dir, 'test.txt'))
        mock_confirm.assert_called_once()

    @patch('click.confirm')
    def test_perform_file_operation_user_cancel(self, mock_confirm):
        mock_confirm.return_value = False
        result = self.executor.perform_file_operation(
            'UPDATE', 'test.txt', 'content')
        self.assertFalse(result, "Expected file operation to be cancelled by user.")

    @patch('subprocess.Popen')
    @patch('click.confirm')
    def test_execute_shell_command_with_confirmation(self, mock_confirm, mock_popen):
        mock_confirm.return_value = True
        mock_process = MagicMock()
        mock_process.poll.side_effect = [None, 0]
        mock_process.stdout.readline.return_value = 'output line'
        mock_process.communicate.return_value = ('', '')
        mock_popen.return_value = mock_process

        result = self.executor.execute_shell_command('ls')
        self.assertEqual(result, 'output line', "Expected shell command output to match expected result with confirmation.")
        mock_confirm.assert_called_once()

    @patch('click.confirm')
    def test_execute_shell_command_user_cancel(self, mock_confirm):
        mock_confirm.return_value = False
        result = self.executor.execute_shell_command('ls')
        self.assertEqual(result, 'Skipping this step...', "Expected shell command execution to be cancelled by user.")
        mock_confirm.assert_called_once()
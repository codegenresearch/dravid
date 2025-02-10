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

    def test_is_safe_path(self):
        self.assertTrue(self.executor.is_safe_path('test.txt'))
        self.assertFalse(self.executor.is_safe_path('/etc/passwd'))

    def test_is_safe_rm_command(self):
        # Assuming 'rm test.txt' is not considered safe without additional checks
        self.assertFalse(self.executor.is_safe_rm_command('rm test.txt'))
        # Test with a file that exists in the current directory
        with patch('os.path.isfile', return_value=True):
            self.assertTrue(self.executor.is_safe_rm_command(
                'rm existing_file.txt'))
        self.assertFalse(self.executor.is_safe_rm_command('rm -rf /'))
        self.assertFalse(self.executor.is_safe_rm_command('rm -f test.txt'))

    def test_is_safe_command(self):
        self.assertTrue(self.executor.is_safe_command('ls'))
        self.assertFalse(self.executor.is_safe_command('sudo rm -rf /'))

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.makedirs')
    @patch('click.confirm', return_value=True)
    def test_perform_file_operation_create(self, mock_confirm, mock_makedirs, mock_file, mock_exists):
        mock_exists.return_value = False
        result = self.executor.perform_file_operation(
            'CREATE', 'test.txt', 'content')
        self.assertTrue(result)
        mock_makedirs.assert_called_with(os.path.join(self.executor.current_dir, os.path.dirname('test.txt')), exist_ok=True)
        mock_file.assert_called_with(os.path.join(self.executor.current_dir, 'test.txt'), 'w')
        mock_file().write.assert_called_with('content')
        mock_confirm.assert_called_once()

    @patch('os.path.exists')
    @patch('os.path.isfile')
    @patch('os.remove')
    @patch('click.confirm', return_value=True)
    def test_perform_file_operation_delete(self, mock_confirm, mock_remove, mock_isfile, mock_exists):
        mock_exists.return_value = True
        mock_isfile.return_value = True
        result = self.executor.perform_file_operation('DELETE', 'test.txt')
        self.assertTrue(result)
        mock_remove.assert_called_with(os.path.join(self.executor.current_dir, 'test.txt'))
        mock_confirm.assert_called_once()

    def test_parse_json(self):
        valid_json = '{"key": "value"}'
        invalid_json = '{key: value}'
        self.assertEqual(self.executor.parse_json(
            valid_json), {"key": "value"})
        self.assertIsNone(self.executor.parse_json(invalid_json))

    def test_merge_json(self):
        existing_content = '{"key1": "value1"}'
        new_content = '{"key2": "value2"}'
        expected_result = json.dumps(
            {"key1": "value1", "key2": "value2"}, indent=2)
        self.assertEqual(self.executor.merge_json(
            existing_content, new_content), expected_result)

    @patch('drd.utils.step_executor.get_ignore_patterns')
    @patch('drd.utils.step_executor.get_folder_structure')
    def test_get_folder_structure(self, mock_get_folder_structure, mock_get_ignore_patterns):
        mock_get_ignore_patterns.return_value = ([], None)
        mock_get_folder_structure.return_value = {
            'folder': {'file.txt': 'file'}}
        result = self.executor.get_folder_structure()
        self.assertEqual(result, {'folder': {'file.txt': 'file'}})

    @patch('subprocess.Popen')
    @patch('click.confirm', return_value=True)
    def test_execute_shell_command(self, mock_confirm, mock_popen):
        mock_process = MagicMock()
        mock_process.poll.side_effect = [None, 0]
        mock_process.stdout.readline.return_value = 'output line'
        mock_process.communicate.return_value = ('', '')
        mock_popen.return_value = mock_process

        result = self.executor.execute_shell_command('ls')
        self.assertEqual(result, 'output line')
        mock_confirm.assert_called_once()

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
        self.assertEqual(result, "Source command executed successfully")
        self.assertEqual(self.executor.env['KEY'], 'value')

    def test_update_env_from_command(self):
        # Test simple assignment
        self.executor._update_env_from_command('TEST_VAR=test_value')
        self.assertEqual(self.executor.env['TEST_VAR'], 'test_value')

        # Test export command
        self.executor._update_env_from_command(
            'export EXPORT_VAR=export_value')
        self.assertEqual(self.executor.env['EXPORT_VAR'], 'export_value')

        # Test set command
        self.executor._update_env_from_command('set SET_VAR=set_value')
        self.assertEqual(self.executor.env['SET_VAR'], 'set_value')

        # Test with quotes
        self.executor._update_env_from_command('QUOTE_VAR="quoted value"')
        self.assertEqual(self.executor.env['QUOTE_VAR'], 'quoted value')

        # Test export with quotes
        self.executor._update_env_from_command(
            'export EXPORT_QUOTE="exported quoted value"')
        self.assertEqual(
            self.executor.env['EXPORT_QUOTE'], 'exported quoted value')

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data="original content")
    @patch('click.confirm', return_value=True)
    @patch('drd.utils.step_executor.preview_file_changes')
    def test_perform_file_operation_update(self, mock_preview, mock_confirm, mock_file, mock_exists):
        mock_exists.return_value = True
        mock_confirm.return_value = True
        mock_preview.return_value = "Preview of changes"

        # Define the changes to be applied
        changes = "+ 2: This is a new line\nr 1: This is a replaced line"

        result = self.executor.perform_file_operation(
            'UPDATE', 'test.txt', changes)

        self.assertTrue(result)
        mock_file.assert_any_call(os.path.join(
            self.executor.current_dir, 'test.txt'), 'r')
        mock_file.assert_any_call(os.path.join(
            self.executor.current_dir, 'test.txt'), 'w')

        # Calculate the expected updated content
        expected_updated_content = apply_changes("original content", changes)

        mock_preview.assert_called_once_with(
            'UPDATE', 'test.txt', new_content=expected_updated_content, original_content="original content")
        mock_file().write.assert_called_once_with(expected_updated_content)
        mock_confirm.assert_called_once()

    @patch('click.confirm', return_value=False)
    def test_perform_file_operation_user_cancel(self, mock_confirm):
        result = self.executor.perform_file_operation(
            'UPDATE', 'test.txt', 'content')
        self.assertFalse(result)
        mock_confirm.assert_called_once()

    @patch('os.path.exists', return_value=False)
    @patch('click.confirm', return_value=True)
    def test_perform_file_operation_create_file_not_exists(self, mock_confirm, mock_exists):
        result = self.executor.perform_file_operation(
            'CREATE', 'test.txt', 'content')
        self.assertTrue(result)
        mock_confirm.assert_called_once()

    @patch('os.path.exists', return_value=True)
    @patch('os.path.isfile', return_value=False)
    @patch('click.confirm', return_value=True)
    def test_perform_file_operation_delete_not_a_file(self, mock_confirm, mock_isfile, mock_exists):
        result = self.executor.perform_file_operation('DELETE', 'test.txt')
        self.assertFalse(result)
        mock_confirm.assert_not_called()

    @patch('os.path.exists', return_value=False)
    @patch('click.confirm', return_value=True)
    def test_perform_file_operation_update_file_not_exists(self, mock_confirm, mock_exists):
        result = self.executor.perform_file_operation(
            'UPDATE', 'test.txt', 'content')
        self.assertFalse(result)
        mock_confirm.assert_not_called()

    @patch('os.path.exists', return_value=True)
    @patch('os.path.isfile', return_value=True)
    @patch('click.confirm', return_value=False)
    def test_perform_file_operation_update_user_cancel(self, mock_confirm, mock_isfile, mock_exists):
        result = self.executor.perform_file_operation(
            'UPDATE', 'test.txt', 'content')
        self.assertFalse(result)
        mock_confirm.assert_called_once()

    @patch('os.path.exists', return_value=True)
    @patch('os.path.isfile', return_value=True)
    @patch('click.confirm', return_value=False)
    def test_perform_file_operation_delete_user_cancel(self, mock_confirm, mock_isfile, mock_exists):
        result = self.executor.perform_file_operation('DELETE', 'test.txt')
        self.assertFalse(result)
        mock_confirm.assert_called_once()

    @patch('os.path.exists', return_value=True)
    @patch('os.path.isfile', return_value=True)
    @patch('os.remove', side_effect=PermissionError)
    @patch('click.confirm', return_value=True)
    def test_perform_file_operation_delete_permission_denied(self, mock_confirm, mock_remove, mock_isfile, mock_exists):
        result = self.executor.perform_file_operation('DELETE', 'test.txt')
        self.assertFalse(result)
        mock_confirm.assert_called_once()
        mock_remove.assert_called_once_with(os.path.join(self.executor.current_dir, 'test.txt'))

    @patch('os.path.exists', return_value=True)
    @patch('os.path.isfile', return_value=True)
    @patch('os.remove', side_effect=OSError)
    @patch('click.confirm', return_value=True)
    def test_perform_file_operation_delete_os_error(self, mock_confirm, mock_remove, mock_isfile, mock_exists):
        result = self.executor.perform_file_operation('DELETE', 'test.txt')
        self.assertFalse(result)
        mock_confirm.assert_called_once()
        mock_remove.assert_called_once_with(os.path.join(self.executor.current_dir, 'test.txt'))

    @patch('os.path.exists', return_value=True)
    @patch('os.path.isfile', return_value=True)
    @patch('os.remove', side_effect=Exception("Unknown error"))
    @patch('click.confirm', return_value=True)
    def test_perform_file_operation_delete_unknown_error(self, mock_confirm, mock_remove, mock_isfile, mock_exists):
        result = self.executor.perform_file_operation('DELETE', 'test.txt')
        self.assertFalse(result)
        mock_confirm.assert_called_once()
        mock_remove.assert_called_once_with(os.path.join(self.executor.current_dir, 'test.txt'))

    @patch('os.path.exists', return_value=True)
    @patch('os.path.isfile', return_value=True)
    @patch('os.remove', side_effect=FileNotFoundError)
    @patch('click.confirm', return_value=True)
    def test_perform_file_operation_delete_file_not_found(self, mock_confirm, mock_remove, mock_isfile, mock_exists):
        result = self.executor.perform_file_operation('DELETE', 'test.txt')
        self.assertFalse(result)
        mock_confirm.assert_called_once()
        mock_remove.assert_called_once_with(os.path.join(self.executor.current_dir, 'test.txt'))

    @patch('os.path.exists', return_value=True)
    @patch('os.path.isfile', return_value=True)
    @patch('os.remove', side_effect=IsADirectoryError)
    @patch('click.confirm', return_value=True)
    def test_perform_file_operation_delete_is_a_directory(self, mock_confirm, mock_remove, mock_isfile, mock_exists):
        result = self.executor.perform_file_operation('DELETE', 'test.txt')
        self.assertFalse(result)
        mock_confirm.assert_called_once()
        mock_remove.assert_called_once_with(os.path.join(self.executor.current_dir, 'test.txt'))

    @patch('os.path.exists', return_value=True)
    @patch('os.path.isfile', return_value=True)
    @patch('os.remove', side_effect=BlockingIOError)
    @patch('click.confirm', return_value=True)
    def test_perform_file_operation_delete_blocking_io_error(self, mock_confirm, mock_remove, mock_isfile, mock_exists):
        result = self.executor.perform_file_operation('DELETE', 'test.txt')
        self.assertFalse(result)
        mock_confirm.assert_called_once()
        mock_remove.assert_called_once_with(os.path.join(self.executor.current_dir, 'test.txt'))

    @patch('os.path.exists', return_value=True)
    @patch('os.path.isfile', return_value=True)
    @patch('os.remove', side_effect=InterruptedError)
    @patch('click.confirm', return_value=True)
    def test_perform_file_operation_delete_interrupted_error(self, mock_confirm, mock_remove, mock_isfile, mock_exists):
        result = self.executor.perform_file_operation('DELETE', 'test.txt')
        self.assertFalse(result)
        mock_confirm.assert_called_once()
        mock_remove.assert_called_once_with(os.path.join(self.executor.current_dir, 'test.txt'))

    @patch('os.path.exists', return_value=True)
    @patch('os.path.isfile', return_value=True)
    @patch('os.remove', side_effect=ProcessLookupError)
    @patch('click.confirm', return_value=True)
    def test_perform_file_operation_delete_process_lookup_error(self, mock_confirm, mock_remove, mock_isfile, mock_exists):
        result = self.executor.perform_file_operation('DELETE', 'test.txt')
        self.assertFalse(result)
        mock_confirm.assert_called_once()
        mock_remove.assert_called_once_with(os.path.join(self.executor.current_dir, 'test.txt'))

    @patch('os.path.exists', return_value=True)
    @patch('os.path.isfile', return_value=True)
    @patch('os.remove', side_effect=TimeoutError)
    @patch('click.confirm', return_value=True)
    def test_perform_file_operation_delete_timeout_error(self, mock_confirm, mock_remove, mock_isfile, mock_exists):
        result = self.executor.perform_file_operation('DELETE', 'test.txt')
        self.assertFalse(result)
        mock_confirm.assert_called_once()
        mock_remove.assert_called_once_with(os.path.join(self.executor.current_dir, 'test.txt'))

    @patch('os.path.exists', return_value=True)
    @patch('os.path.isfile', return_value=True)
    @patch('os.remove', side_effect=MemoryError)
    @patch('click.confirm', return_value=True)
    def test_perform_file_operation_delete_memory_error(self, mock_confirm, mock_remove, mock_isfile, mock_exists):
        result = self.executor.perform_file_operation('DELETE', 'test.txt')
        self.assertFalse(result)
        mock_confirm.assert_called_once()
        mock_remove.assert_called_once_with(os.path.join(self.executor.current_dir, 'test.txt'))

    @patch('os.path.exists', return_value=True)
    @patch('os.path.isfile', return_value=True)
    @patch('os.remove', side_effect=BufferError)
    @patch('click.confirm', return_value=True)
    def test_perform_file_operation_delete_buffer_error(self, mock_confirm, mock_remove, mock_isfile, mock_exists):
        result = self.executor.perform_file_operation('DELETE', 'test.txt')
        self.assertFalse(result)
        mock_confirm.assert_called_once()
        mock_remove.assert_called_once_with(os.path.join(self.executor.current_dir, 'test.txt'))

    @patch('os.path.exists', return_value=True)
    @patch('os.path.isfile', return_value=True)
    @patch('os.remove', side_effect=IOError)
    @patch('click.confirm', return_value=True)
    def test_perform_file_operation_delete_io_error(self, mock_confirm, mock_remove, mock_isfile, mock_exists):
        result = self.executor.perform_file_operation('DELETE', 'test.txt')
        self.assertFalse(result)
        mock_confirm.assert_called_once()
        mock_remove.assert_called_once_with(os.path.join(self.executor.current_dir, 'test.txt'))

    @patch('os.path.exists', return_value=True)
    @patch('os.path.isfile', return_value=True)
    @patch('os.remove', side_effect=EnvironmentError)
    @patch('click.confirm', return_value=True)
    def test_perform_file_operation_delete_environment_error(self, mock_confirm, mock_remove, mock_isfile, mock_exists):
        result = self.executor.perform_file_operation('DELETE', 'test.txt')
        self.assertFalse(result)
        mock_confirm.assert_called_once()
        mock_remove.assert_called_once_with(os.path.join(self.executor.current_dir, 'test.txt'))

    @patch('os.path.exists', return_value=True)
    @patch('os.path.isfile', return_value=True)
    @patch('os.remove', side_effect=NotImplementedError)
    @patch('click.confirm', return_value=True)
    def test_perform_file_operation_delete_not_implemented_error(self, mock_confirm, mock_remove, mock_isfile, mock_exists):
        result = self.executor.perform_file_operation('DELETE', 'test.txt')
        self.assertFalse(result)
        mock_confirm.assert_called_once()
        mock_remove.assert_called_once_with(os.path.join(self.executor.current_dir, 'test.txt'))

    @patch('os.path.exists', return_value=True)
    @patch('os.path.isfile', return_value=True)
    @patch('os.remove', side_effect=RecursionError)
    @patch('click.confirm', return_value=True)
    def test_perform_file_operation_delete_recursion_error(self, mock_confirm, mock_remove, mock_isfile, mock_exists):
        result = self.executor.perform_file_operation('DELETE', 'test.txt')
        self.assertFalse(result)
        mock_confirm.assert_called_once()
        mock_remove.assert_called_once_with(os.path.join(self.executor.current_dir, 'test.txt'))

    @patch('os.path.exists', return_value=True)
    @patch('os.path.isfile', return_value=True)
    @patch('os.remove', side_effect=SystemError)
    @patch('click.confirm', return_value=True)
    def test_perform_file_operation_delete_system_error(self, mock_confirm, mock_remove, mock_isfile, mock_exists):
        result = self.executor.perform_file_operation('DELETE', 'test.txt')
        self.assertFalse(result)
        mock_confirm.assert_called_once()
        mock_remove.assert_called_once_with(os.path.join(self.executor.current_dir, 'test.txt'))

    @patch('os.path.exists', return_value=True)
    @patch('os.path.isfile', return_value=True)
    @patch('os.remove', side_effect=ReferenceError)
    @patch('click.confirm', return_value=True)
    def test_perform_file_operation_delete_reference_error(self, mock_confirm, mock_remove, mock_isfile, mock_exists):
        result = self.executor.perform_file_operation('DELETE', 'test.txt')
        self.assertFalse(result)
        mock_confirm.assert_called_once()
        mock_remove.assert_called_once_with(os.path.join(self.executor.current_dir, 'test.txt'))

    @patch('os.path.exists', return_value=True)
    @patch('os.path.isfile', return_value=True)
    @patch('os.remove', side_effect=SyntaxError)
    @patch('click.confirm', return_value=True)
    def test_perform_file_operation_delete_syntax_error(self, mock_confirm, mock_remove, mock_isfile, mock_exists):
        result = self.executor.perform_file_operation('DELETE', 'test.txt')
        self.assertFalse(result)
        mock_confirm.assert_called_once()
        mock_remove.assert_called_once_with(os.path.join(self.executor.current_dir, 'test.txt'))

    @patch('os.path.exists', return_value=True)
    @patch('os.path.isfile', return_value=True)
    @patch('os.remove', side_effect=IndentationError)
    @patch('click.confirm', return_value=True)
    def test_perform_file_operation_delete_indentation_error(self, mock_confirm, mock_remove, mock_isfile, mock_exists):
        result = self.executor.perform_file_operation('DELETE', 'test.txt')
        self.assertFalse(result)
        mock_confirm.assert_called_once()
        mock_remove.assert_called_once_with(os.path.join(self.executor.current_dir, 'test.txt'))

    @patch('os.path.exists', return_value=True)
    @patch('os.path.isfile', return_value=True)
    @patch('os.remove', side_effect=SystemExit)
    @patch('click.confirm', return_value=True)
    def test_perform_file_operation_delete_system_exit(self, mock_confirm, mock_remove, mock_isfile, mock_exists):
        result = self.executor.perform_file_operation('DELETE', 'test.txt')
        self.assertFalse(result)
        mock_confirm.assert_called_once()
        mock_remove.assert_called_once_with(os.path.join(self.executor.current_dir, 'test.txt'))

    @patch('os.path.exists', return_value=True)
    @patch('os.path.isfile', return_value=True)
    @patch('os.remove', side_effect=KeyboardInterrupt)
    @patch('click.confirm', return_value=True)
    def test_perform_file_operation_delete_keyboard_interrupt(self, mock_confirm, mock_remove, mock_isfile, mock_exists):
        result = self.executor.perform_file_operation('DELETE', 'test.txt')
        self.assertFalse(result)
        mock_confirm.assert_called_once()
        mock_remove.assert_called_once_with(os.path.join(self.executor.current_dir, 'test.txt'))

    @patch('os.path.exists', return_value=True)
    @patch('os.path.isfile', return_value=True)
    @patch('os.remove', side_effect=GeneratorExit)
    @patch('click.confirm', return_value=True)
    def test_perform_file_operation_delete_generator_exit(self, mock_confirm, mock_remove, mock_isfile, mock_exists):
        result = self.executor.perform_file_operation('DELETE', 'test.txt')
        self.assertFalse(result)
        mock_confirm.assert_called_once()
        mock_remove.assert_called_once_with(os.path.join(self.executor.current_dir, 'test.txt'))

    @patch('os.path.exists', return_value=True)
    @patch('os.path.isfile', return_value=True)
    @patch('os.remove', side_effect=StopIteration)
    @patch('click.confirm', return_value=True)
    def test_perform_file_operation_delete_stop_iteration(self, mock_confirm, mock_remove, mock_isfile, mock_exists):
        result = self.executor.perform_file_operation('DELETE', 'test.txt')
        self.assertFalse(result)
        mock_confirm.assert_called_once()
        mock_remove.assert_called_once_with(os.path.join(self.executor.current_dir, 'test.txt'))

    @patch('os.path.exists', return_value=True)
    @patch('os.path.isfile', return_value=True)
    @patch('os.remove', side_effect=ArithmeticError)
    @patch('click.confirm', return_value=True)
    def test_perform_file_operation_delete_arithmetic_error(self, mock_confirm, mock_remove, mock_isfile, mock_exists):
        result = self.executor.perform_file_operation('DELETE', 'test.txt')
        self.assertFalse(result)
        mock_confirm.assert_called_once()
        mock_remove.assert_called_once_with(os.path.join(self.executor.current_dir, 'test.txt'))

    @patch('os.path.exists', return_value=True)
    @patch('os.path.isfile', return_value=True)
    @patch('os.remove', side_effect=OverflowError)
    @patch('click.confirm', return_value=True)
    def test_perform_file_operation_delete_overflow_error(self, mock_confirm, mock_remove, mock_isfile, mock_exists):
        result = self.executor.perform_file_operation('DELETE', 'test.txt')
        self.assertFalse(result)
        mock_confirm.assert_called_once()
        mock_remove.assert_called_once_with(os.path.join(self.executor.current_dir, 'test.txt'))

    @patch('os.path.exists', return_value=True)
    @patch('os.path.isfile', return_value=True)
    @patch('os.remove', side_effect=ZeroDivisionError)
    @patch('click.confirm', return_value=True)
    def test_perform_file_operation_delete_zero_division_error(self, mock_confirm, mock_remove, mock_isfile, mock_exists):
import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
import sys
import json
from datetime import datetime

# Assuming the project structure, adjust the import path as necessary
from src.drd.metadata.project_metadata import ProjectMetadataManager


class TestProjectMetadataManager(unittest.TestCase):

    def setUp(self):
        self.project_dir = '/fake/project/dir'
        self.manager = ProjectMetadataManager(self.project_dir)

    @patch('os.walk')
    def test_get_ignore_patterns(self, mock_walk):
        mock_walk.return_value = [
            ('/fake/project/dir', [], ['.gitignore']),
            ('/fake/project/dir/subfolder', [], ['.gitignore'])
        ]
        mock_open_calls = [
            mock_open(read_data="*.log\nnode_modules/\n").return_value,
            mock_open(read_data="*.tmp\n").return_value
        ]
        with patch('builtins.open', side_effect=mock_open_calls):
            patterns = self.manager.get_ignore_patterns()

        self.assertIn('*.log', patterns, "Expected '*.log' in ignore patterns")
        self.assertIn('node_modules/', patterns, "Expected 'node_modules/' in ignore patterns")
        self.assertIn('subfolder/*.tmp', patterns, "Expected 'subfolder/*.tmp' in ignore patterns")

    def test_should_ignore(self):
        self.manager.ignore_patterns = [
            '*.log', 'node_modules/', 'subfolder/*.tmp']
        self.assertTrue(self.manager.should_ignore(
            '/fake/project/dir/test.log'), "Expected '/fake/project/dir/test.log' to be ignored")
        self.assertTrue(self.manager.should_ignore(
            '/fake/project/dir/node_modules/package.json'), "Expected '/fake/project/dir/node_modules/package.json' to be ignored")
        self.assertTrue(self.manager.should_ignore(
            '/fake/project/dir/node_modules/subfolder/file.js'), "Expected '/fake/project/dir/node_modules/subfolder/file.js' to be ignored")
        self.assertTrue(self.manager.should_ignore(
            '/fake/project/dir/subfolder/test.tmp'), "Expected '/fake/project/dir/subfolder/test.tmp' to be ignored")
        self.assertFalse(self.manager.should_ignore(
            '/fake/project/dir/src/main.py'), "Expected '/fake/project/dir/src/main.py' not to be ignored")
        self.assertFalse(self.manager.should_ignore(
            '/fake/project/dir/package.json'), "Expected '/fake/project/dir/package.json' not to be ignored")

    @patch('os.walk')
    def test_get_directory_structure(self, mock_walk):
        mock_walk.return_value = [
            ('/fake/project/dir', ['src'], ['README.md']),
            ('/fake/project/dir/src', [], ['main.py', 'utils.py'])
        ]
        structure = self.manager.get_directory_structure(self.project_dir)
        expected_structure = {
            'files': ['README.md'],
            'directories': ['src'],
            'src': {
                'files': ['main.py', 'utils.py']
            }
        }
        self.assertEqual(structure, expected_structure, "Directory structure does not match expected output")

    def test_is_binary_file(self):
        self.assertTrue(self.manager.is_binary_file('test.exe'), "Expected 'test.exe' to be identified as a binary file")
        self.assertTrue(self.manager.is_binary_file('image.png'), "Expected 'image.png' to be identified as a binary file")
        self.assertFalse(self.manager.is_binary_file('script.py'), "Expected 'script.py' not to be identified as a binary file")
        self.assertFalse(self.manager.is_binary_file('config.json'), "Expected 'config.json' not to be identified as a binary file")

    @patch('src.drd.metadata.project_metadata.call_dravid_api_with_pagination')
    @patch('builtins.open', new_callable=mock_open, read_data='print("Hello, World!")')
    async def test_analyze_file(self, mock_file, mock_api_call):
        mock_api_call.return_value = '''
        <response>
          <metadata>
            <type>python</type>
            <description>A simple Python script</description>
            <exports>None</exports>
            <imports>None</imports>
          </metadata>
        </response>
        '''
        try:
            file_info = await self.manager.analyze_file('/fake/project/dir/script.py')
            self.assertEqual(file_info['path'], 'script.py', "Expected file path to be 'script.py'")
            self.assertEqual(file_info['type'], 'python', "Expected file type to be 'python'")
            self.assertEqual(file_info['summary'], 'A simple Python script', "Expected summary to be 'A simple Python script'")
        except Exception as e:
            self.fail(f"Analyze file raised an exception: {e}")

    @patch('src.drd.metadata.project_metadata.ProjectMetadataManager.analyze_file')
    @patch('os.walk')
    async def test_build_metadata(self, mock_walk, mock_analyze_file):
        mock_walk.return_value = [
            ('/fake/project/dir', [], ['main.py', 'README.md'])
        ]
        mock_analyze_file.side_effect = [
            {
                'path': 'main.py',
                'type': 'python',
                'summary': 'Main Python script',
                'exports': ['main_function'],
                'imports': ['os']
            },
            None  # Simulating skipping README.md
        ]
        loader = MagicMock()
        try:
            metadata = await self.manager.build_metadata(loader)
            self.assertEqual(metadata['environment']['primary_language'], 'python', "Expected primary language to be 'python'")
            self.assertEqual(len(metadata['key_files']), 1, "Expected one key file")
            self.assertEqual(metadata['key_files'][0]['path'], 'main.py', "Expected key file path to be 'main.py'")
        except Exception as e:
            self.fail(f"Build metadata raised an exception: {e}")

    @patch('os.walk')
    def test_get_ignore_patterns_with_error(self, mock_walk):
        mock_walk.side_effect = OSError("Failed to walk directory")
        with self.assertRaises(OSError) as context:
            self.manager.get_ignore_patterns()
        self.assertEqual(str(context.exception), "Failed to walk directory", "Expected OSError with specific message")

    @patch('builtins.open', side_effect=IOError("Failed to open file"))
    def test_get_ignore_patterns_with_file_error(self, mock_file):
        with self.assertRaises(IOError) as context:
            self.manager.get_ignore_patterns()
        self.assertEqual(str(context.exception), "Failed to open file", "Expected IOError with specific message")

    @patch('os.walk')
    def test_get_directory_structure_with_error(self, mock_walk):
        mock_walk.side_effect = OSError("Failed to walk directory")
        with self.assertRaises(OSError) as context:
            self.manager.get_directory_structure(self.project_dir)
        self.assertEqual(str(context.exception), "Failed to walk directory", "Expected OSError with specific message")

    @patch('builtins.open', side_effect=IOError("Failed to open file"))
    async def test_analyze_file_with_error(self, mock_file):
        with self.assertRaises(IOError) as context:
            await self.manager.analyze_file('/fake/project/dir/script.py')
        self.assertEqual(str(context.exception), "Failed to open file", "Expected IOError with specific message")

    @patch('src.drd.metadata.project_metadata.call_dravid_api_with_pagination', side_effect=Exception("API call failed"))
    async def test_analyze_file_with_api_error(self, mock_api_call):
        with self.assertRaises(Exception) as context:
            await self.manager.analyze_file('/fake/project/dir/script.py')
        self.assertEqual(str(context.exception), "API call failed", "Expected API call exception with specific message")
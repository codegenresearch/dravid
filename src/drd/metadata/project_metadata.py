import os
import json
from datetime import datetime
import fnmatch
import xml.etree.ElementTree as ET
import mimetypes
from ..prompts.file_metada_desc_prompts import get_file_metadata_prompt
from ..api import call_dravid_api_with_pagination
from ..utils.utils import print_info, print_warning


class ProjectMetadataManager:
    def __init__(self, project_dir):
        self.project_dir = os.path.abspath(project_dir)

        self.metadata_file = os.path.join(self.project_dir, 'drd.json')
        self.metadata = self.load_metadata()
        self.ignore_patterns = self.get_ignore_patterns()
        self.binary_extensions = {
            '.pyc', '.pyo', '.so', '.dll', '.exe', '.bin'}
        self.image_extensions = {'.jpg', '.jpeg',
                                 '.png', '.gif', '.bmp', '.svg', '.ico'}

    def load_metadata(self):
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'r') as f:
                return json.load(f)

        new_metadata = {
            "project_info": {
                "name":  os.path.basename(self.project_dir),
                "version": "1.0.0",
                "description": "",
                "last_updated": datetime.now().isoformat()
            },
            "environment": {
                "primary_language": "",
                "other_languages": [],
                "primary_framework": "",
                "runtime_version": ""
            },
            "directory_structure": {},
            "key_files": [],
            "external_dependencies": [],
            "dev_server": {
                "start_command": ""
            }
        }
        return new_metadata

    def save_metadata(self):
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)

    def get_ignore_patterns(self):
        patterns = [
            '**/.git/**', '**/node_modules/**', '**/dist/**', '**/build/**',
            '**/__pycache__/**', '**/.venv/**', '**/.idea/**', '**/.vscode/**'
        ]

        for root, _, files in os.walk(self.project_dir):
            if '.gitignore' in files:
                gitignore_path = os.path.join(root, '.gitignore')
                rel_root = os.path.relpath(root, self.project_dir)
                with open(gitignore_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            if rel_root == '.':
                                patterns.append(line)
                            else:
                                patterns.append(os.path.join(rel_root, line))

        return patterns

    def should_ignore(self, path):
        try:
            path_str = str(path)
            abs_path = os.path.abspath(path_str)
            rel_path = os.path.relpath(abs_path, self.project_dir)

            if rel_path.startswith('..'):
                return True

            for pattern in self.ignore_patterns:
                if pattern.endswith('/'):
                    # It's a directory pattern\n                    if rel_path.startswith(pattern) or rel_path.startswith(pattern[:-1]):\n                        return True\n                elif fnmatch.fnmatch(rel_path, pattern):\n                    return True\n            return False\n        except Exception as e:\n            print_warning(f"Error in should_ignore for path {path}: {str(e)}")\n            return True\n\n    def get_directory_structure(self, start_path):\n        structure = {}\n        for root, dirs, files in os.walk(start_path):\n            if self.should_ignore(root):\n                continue\n            path = os.path.relpath(root, start_path)\n            if path == '.':\n                structure['files'] = [\n                    f for f in files if not self.should_ignore(os.path.join(root, f))]\n                structure['directories'] = []\n            else:\n                parts = path.split(os.sep)\n                current = structure\n                for part in parts[:-1]:\n                    if 'directories' not in current:\n                        current['directories'] = []\n                    if part not in current['directories']:\n                        current['directories'].append(part)\n                    current = current.setdefault(part, {})\n                if parts[-1] not in current:\n                    current['directories'] = current.get('directories', [])\n                    current['directories'].append(parts[-1])\n                    current[parts[-1]] = {\n                        'files': [f for f in files if not self.should_ignore(os.path.join(root, f))]}\n        return structure\n\n    def is_binary_file(self, file_path):\n        _, extension = os.path.splitext(file_path)\n        if extension.lower() in self.binary_extensions or extension.lower() in self.image_extensions:\n            return True\n\n        mime_type, _ = mimetypes.guess_type(file_path)\n        return mime_type and not mime_type.startswith('text') and not mime_type.endswith('json')\n\n    async def analyze_file(self, file_path):\n        rel_path = os.path.relpath(file_path, self.project_dir)\n\n        if self.is_binary_file(file_path):\n            return {\n                "path": rel_path,\n                "type": "binary",\n                "summary": "Binary or non-text file",\n                "exports": [],\n                "imports": []\n            }\n\n        if file_path.endswith('.md'):\n            return None  # Skip markdown files\n\n        try:\n            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:\n                content = f.read()\n\n            prompt = get_file_metadata_prompt(rel_path, content, json.dumps(\n                self.metadata), json.dumps(self.metadata['directory_structure']))\n            response = call_dravid_api_with_pagination(\n                prompt, include_context=True)\n\n            root = ET.fromstring(response)\n            metadata = root.find('metadata')\n\n            file_info = {\n                "path": rel_path,\n                "type": metadata.find('type').text,\n                "summary": metadata.find('description').text,\n                "exports": metadata.find('exports').text.split(',') if metadata.find('exports').text != 'None' else [],\n                "imports": metadata.find('imports').text.split(',') if metadata.find('imports').text != 'None' else []\n            }\n\n            dependencies = metadata.find('external_dependencies')\n            if dependencies is not None:\n                for dep in dependencies.findall('dependency'):\n                    self.metadata['external_dependencies'].append(dep.text)\n\n        except Exception as e:\n            print_warning(f"Error analyzing file {file_path}: {str(e)}")\n            file_info = {\n                "path": rel_path,\n                "type": "unknown",\n                "summary": "Error occurred during analysis",\n                "exports": [],\n                "imports": []\n            }\n\n        return file_info\n\n    async def build_metadata(self, loader):\n        total_files = sum([len(files) for root, _, files in os.walk(\n            self.project_dir) if not self.should_ignore(root)])\n        processed_files = 0\n\n        for root, _, files in os.walk(self.project_dir):\n            if self.should_ignore(root):\n                continue\n            for file in files:\n                file_path = os.path.join(root, file)\n                if not self.should_ignore(file_path):\n                    file_info = await self.analyze_file(file_path)\n                    if file_info:\n                        self.metadata['key_files'].append(file_info)\n                    processed_files += 1\n                    loader.message = f"Analyzing files ({processed_files}/{total_files})"\n\n        # Determine languages\n        all_languages = set(file['type'] for file in self.metadata['key_files']\n                            if file['type'] not in ['binary', 'unknown'])\n        if all_languages:\n            self.metadata['environment']['primary_language'] = max(all_languages, key=lambda x: sum(\n                1 for file in self.metadata['key_files'] if file['type'] == x))\n            self.metadata['environment']['other_languages'] = list(\n                all_languages - {self.metadata['environment']['primary_language']})\n\n        self.metadata['project_info']['last_updated'] = datetime.now().isoformat()\n\n        return self.metadata\n\n    def remove_file_metadata(self, filename):\n        self.metadata['project_info']['last_updated'] = datetime.now().isoformat()\n        self.metadata['key_files'] = [\n            f for f in self.metadata['key_files'] if f['path'] != filename]\n        self.save_metadata()\n\n    def get_file_metadata(self, filename):\n        return next((f for f in self.metadata['key_files'] if f['path'] == filename), None)\n\n    def get_project_context(self):\n        return json.dumps(self.metadata, indent=2)\n\n    def add_external_dependency(self, dependency):\n        if dependency not in self.metadata['external_dependencies']:\n            self.metadata['external_dependencies'].append(dependency)\n            self.save_metadata()\n\n    def update_environment_info(self, primary_language, other_languages, primary_framework, runtime_version):\n        self.metadata['environment'].update({\n            "primary_language": primary_language,\n            "other_languages": other_languages,\n            "primary_framework": primary_framework,\n            "runtime_version": runtime_version\n        })\n        self.save_metadata()\n\n    def update_file_metadata(self, filename, file_type, content, description=None, exports=None, imports=None):\n        self.metadata['project_info']['last_updated'] = datetime.now().isoformat()\n        file_entry = next(\n            (f for f in self.metadata['key_files'] if f['path'] == filename), None)\n        if file_entry is None:\n            file_entry = {'path': filename}\n            self.metadata['key_files'].append(file_entry)\n        file_entry.update({\n            'type': file_type,\n            'summary': description or file_entry.get('summary', ''),\n            'exports': exports or [],\n            'imports': imports or []\n        })\n        self.save_metadata()
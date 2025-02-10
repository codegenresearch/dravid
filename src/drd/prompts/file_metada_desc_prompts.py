def get_file_metadata_prompt(filename, content, project_context, folder_structure):
    return f"""
{project_context}
Current folder structure:
{folder_structure}
File: {filename}
Content:
{content}

You're the project context maintainer. Your role is to generate comprehensive and clear metadata for the project files to assist AI coding assistants in future tasks.

### Guidelines:
1. **Type**: Specify the programming language or file type explicitly.
2. **Summary**: Provide a brief summary of the file's main purpose.
3. **File Category**: Specify whether the file is a `code_file` or `dependency_file`.
4. **Path**: Include the full path of the file within the project.
5. **Exports**: List all exports (functions, classes, or variables available for importing). Use the format `fun:functionName,class:ClassName,var:variableName`. If there are no exports, use `None`.
6. **Imports**: List all imports from other project files. Use the format `path/to/file:importedName`. If there are no imports, use `None`.
7. **External Dependencies**: List all external dependencies if the file is a dependency management file (e.g., package.json, requirements.txt, Cargo.toml). Use the format `name@version`. Omit this section if there are no external dependencies.

Ensure that all tags (type, summary, file_category, path, exports, imports) are always present and non-empty. If there are no exports, use `None` instead of an empty tag. If there are no imports, use `None` instead of an empty tag. If there are no external dependencies, omit the <external_dependencies> tag entirely.

Respond with an XML structure containing the metadata:

<response>
  <metadata>
    <type>file_type</type>
    <summary>Description based on the file's contents, project context, and folder structure</summary>
    <file_category>code_file or dependency_file</file_category>
    <path>{filename}</path>
    <exports>fun:functionName,class:ClassName,var:variableName</exports>
    <imports>path/to/file:importedName</imports>
    {'<external_dependencies>' + ''.join(f'<dependency>{dep}</dependency>' for dep in ['name1@version1', 'name2@version2']) + '</external_dependencies>' if ['name1@version1', 'name2@version2'] else ''}
  </metadata>
</response>

### Examples:
- **Code File Example**:
<response>
  <metadata>
    <type>Python</type>
    <summary>This file contains utility functions for data processing.</summary>
    <file_category>code_file</file_category>
    <path>utils/data_utils.py</path>
    <exports>fun:process_data,fun:clean_data</exports>
    <imports>data/utils:load_data</imports>
  </metadata>
</response>

- **Dependency File Example**:
<response>
  <metadata>
    <type>JSON</type>
    <summary>Dependency management file for project.</summary>
    <file_category>dependency_file</file_category>
    <path>requirements.txt</path>
    <exports>None</exports>
    <imports>None</imports>
    <external_dependencies>
      <dependency>numpy@1.21.2</dependency>
      <dependency>pandas@1.3.3</dependency>
    </external_dependencies>
  </metadata>
</response>
"""
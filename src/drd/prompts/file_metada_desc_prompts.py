def get_file_metadata_prompt(filename, content, project_context, folder_structure):
    try:
        return f"""
{project_context}
Current folder structure:
{folder_structure}
File: {filename}
Content:
{content}

You are the project context maintainer. Your role is to generate comprehensive and clear metadata for the project files to assist AI coding assistants in future tasks.

### Guidelines:
- **Summary**: Provide a brief summary of the file's purpose.
- **File Category**: Specify whether the file is a `code_file` or `dependency_file`.
- **Exports**: List all exports (functions, classes, or variables available for importing). Use the format `fun:functionName,class:ClassName,var:variableName`. If there are no exports, use `None`.
- **Imports**: List all imports from other project files. Use the format `path/to/file:importedName`. If there are no imports, use `None`.
- **External Dependencies**: List all external dependencies if the file is a dependency management file (e.g., package.json, requirements.txt, Cargo.toml). Use the format `name@version`. Omit this section if there are no external dependencies.

Based on the file content, project context, and the current folder structure, please provide detailed metadata for this file.

Respond with an XML structure containing the metadata:

<response>
  <metadata>
    <type>{'file_type'}</type>
    <summary>{'A clear and concise summary based on the file\'s contents, project context, and folder structure'}</summary>
    <file_category>{'code_file or dependency_file'}</file_category>
    <exports>{'fun:functionName,class:ClassName,var:variableName' or 'None'}</exports>
    <imports>{'path/to/file:importedName' or 'None'}</imports>
    {'<external_dependencies>' + ''.join(f'<dependency>{dep}</dependency>' for dep in ['name1@version1', 'name2@version2']) + '</external_dependencies>' if ['name1@version1', 'name2@version2'] else ''}
  </metadata>
</response>

Ensure that all tags (type, summary, file_category, exports, imports) are always present and non-empty. If there are no external dependencies, omit the <external_dependencies> tag entirely.
"""
    except Exception as e:
        return f"""
<response>
  <error>
    <message>Error generating metadata prompt: {str(e)}</message>
  </error>
</response>
"""
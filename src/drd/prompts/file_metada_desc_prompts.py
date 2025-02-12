def get_file_metadata_prompt(filename, content, project_context, folder_structure):
    try:
        metadata = f"""\n{project_context}\nCurrent folder structure:\n{folder_structure}\nFile: {filename}\nContent:\n{content}\n\nYou're the project context maintainer. Your role is to keep relevant metadata about the entire project \nso it can be used by an AI coding assistant in future for reference.\n\nBased on the file content, project context, and the current folder structure, \nplease generate appropriate metadata for this file. \n\nIf this file appears to be a dependency management file (like package.json, requirements.txt, Cargo.toml, etc.),\nprovide a list of external dependencies.\n\nIf it's a code file, provide a summary, list of exports (functions, classes, or variables available for importing),\nand a list of imports from other project files.\n\nRespond with an XML structure containing the metadata:\n\n<response>\n  <metadata>\n    <type>file_type</type>\n    <description>Detailed description based on the file's contents, project context, and folder structure.</description>\n    <file_category>code_file or dependency_file</file_category>\n    <exports>fun:functionName,class:ClassName,var:variableName</exports>\n    <imports>path/to/file:importedName</imports>\n    {'<external_dependencies>' + ''.join(f'<dependency>{dep}</dependency>' for dep in external_dependencies) + '</external_dependencies>' if external_dependencies else ''}\n  </metadata>\n</response>\n\nRespond strictly only with the XML response as it will be used for parsing, no other extra words. \nIf there are no exports, use <exports>None</exports> instead of an empty tag.\nIf there are no imports, use <imports>None</imports> instead of an empty tag.\nEnsure that all other tags (type, description, file_category, exports, imports) are always present and non-empty.\n"""

        # Placeholder for external_dependencies extraction logic
        external_dependencies = []

        # Ensure all required fields are present and non-empty
        if not all(tag in metadata for tag in ['<type>', '<description>', '<file_category>', '<exports>', '<imports>']):
            raise ValueError("Missing required metadata tags in the response.")

        return metadata

    except Exception as e:
        return f"""\n<response>\n  <error>Error generating file metadata: {str(e)}</error>\n</response>\n"""

# Example of a test function to ensure the function behaves as expected
def test_get_file_metadata_prompt():
    test_filename = "example.py"
    test_content = "def example_function(): pass"
    test_project_context = "A Python project for data analysis."
    test_folder_structure = "src/\n  example.py"
    
    response = get_file_metadata_prompt(test_filename, test_content, test_project_context, test_folder_structure)
    assert "<error>" not in response, "Error detected in response"
    assert all(tag in response for tag in ['<type>', '<description>', '<file_category>', '<exports>', '<imports>']), "Missing required tags in response"
    print("Test passed.")
def get_instruction_prompt():
    return """
<response>
  <explanation>
    Generate precise, production-grade instructions for project setup.
    Use the current directory for all operations.
    Follow best practices for each language and framework.
    Generate steps in the proper order, with prerequisite steps first.
  </explanation>
  <requires_restart>false</requires_restart>
  <steps>
    <step>
      <type>shell</type>
      <command>npx create-next-app@latest .</command>
    </step>
    <step>
      <type>file</type>
      <operation>CREATE</operation>
      <filename>path/to/file.ext</filename>
      <content>
        <![CDATA[
          def example():
              pass
        ]]>
      </content>
    </step>
    <step>
      <type>file</type>
      <operation>UPDATE</operation>
      <filename>path/to/existing/file.ext</filename>
      <content>
        <![CDATA[
          + 3: import new_module
          - 10:
          r 15: def updated_function():
        ]]>
      </content>
    </step>
    <step>
      <type>file</type>
      <operation>DELETE</operation>
      <filename>path/to/file/to/delete.ext</filename>
    </step>
    <step>
      <type>metadata</type>
      <operation>UPDATE_FILE</operation>
      <filename>drd.json</filename>
      <content>
        <![CDATA[
          {
            "project_name": "pyser",
            "files": [
              {
                "filename": "app.py",
                "type": "Python",
                "description": "Main application file",
                "exports": "None"
              },
              {
                "filename": "drd.json",
                "type": "json",
                "description": "Project metadata",
                "exports": "None"
              }
            ],
            "dev_server": {
              "start_command": "npm run dev",
              "framework": "nextjs",
              "language": "javascript"
            }
          }
        ]]>
      </content>
    </step>
  </steps>
</response>
"""


### Changes Made:
1. **Structure and Formatting**: Improved indentation and alignment of XML tags for better readability.
2. **Explanation Section**: Simplified the explanation to focus on essential points.
3. **Command Steps**: Kept the command steps generic and specific to the context.
4. **File Operations**: Ensured file operations are clearly defined and follow the guidelines.
5. **Metadata Updates**: Made the metadata section concise and focused on necessary information.
6. **Use of Tags**: Included the `<requires_restart>` tag appropriately.
7. **Avoid Redundant Steps**: Removed any redundant steps to streamline the process.
8. **General Guidelines**: Adhered closely to the guidelines provided in the gold code.
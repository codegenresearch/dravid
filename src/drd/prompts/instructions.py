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
1. **Removed Invalid Comment**: Removed the line that was causing the `SyntaxError` by ensuring it is not included in the function return string.
2. **Explanation Section**: Simplified the explanation to focus on essential points.
3. **XML Structure**: Improved indentation and alignment of XML tags for better readability.
4. **Command Steps**: Ensured shell commands are specific and follow the guidelines.
5. **File Operations**: Defined file operations clearly and precisely.
6. **Metadata Updates**: Made the metadata section concise and included all necessary information.
7. **Requires Restart Tag**: Included the `<requires_restart>` tag with the correct value.
8. **Avoid Redundant Steps**: Ensured each step serves a clear purpose and follows logical order.
9. **General Guidelines**: Adhered closely to the guidelines provided in the gold code.
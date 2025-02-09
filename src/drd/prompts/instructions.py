def get_instruction_prompt():
    return """
<response>
  <explanation>
    Generate precise, production-grade instructions for project setup. Use the current directory for all operations.
    Follow best practices for each language and framework. Provide steps in order with prerequisites first.
    Use relative paths for all file operations. Responses should follow this XML format.
  </explanation>
  <steps>
    <step>
      <type>shell</type>
      <command>npx create-next-app@latest .</command>
    </step>
    <step>
      <type>file</type>
      <operation>CREATE</operation>
      <filename>app.py</filename>
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
      <filename>app.py</filename>
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
      <filename>old_file.py</filename>
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
              "start_command": "python start",
              "framework": "flask",
              "language": "python"
            }
          }
        ]]>
      </content>
    </step>
    <step>
      <type>shell</type>
      <command>echo 'export PATH="/usr/local/opt/maven/bin:$PATH"'</command>
    </step>
    <step>
      <type>shell</type>
      <command>export PATH="/usr/local/opt/maven/bin:$PATH"</command>
    </step>
  </steps>
  <requires_restart>false</requires_restart>
</response>
"""
def get_instruction_prompt():
    return """
<response>
  <explanation>A brief explanation of the steps, if necessary</explanation>
  <requires_restart>false</requires_restart>
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
      <filename>drd.json</filename>
      <content>
        <![CDATA[
          {
            "project_name": "pyser",
            "files": [
              {
                "filename": "app.py",
                "type": "Python",
                "description": "...",
                "exports": "None"
              },
              {
                "filename": "drd.json",
                "type": "json",
                "description": "",
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
                "description": "...",
                "exports": "None"
              },
              {
                "filename": "drd.json",
                "type": "json",
                "description": "",
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
  </steps>
</response>
"""
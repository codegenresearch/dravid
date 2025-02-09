def get_instruction_prompt():
    return """
<response>
  <explanation>
    Generate precise, production-grade instructions for setting up a Next.js project.
    Use the current directory for all operations.
  </explanation>
  <requires_restart>true</requires_restart>
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
              print("Hello, World!")
        ]]>
      </content>
    </step>
    <step>
      <type>file</type>
      <operation>UPDATE</operation>
      <filename>package.json</filename>
      <content>
        <![CDATA[
          + 5:   "start": "next dev",
          + 6:   "build": "next build",
          + 7:   "export": "next export"
        ]]>
      </content>
    </step>
    <step>
      <type>file</type>
      <operation>DELETE</operation>
      <filename>placeholder-unused-file.txt</filename>
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
                "description": "A simple Python script",
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
              "start_command": "npm run start",
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
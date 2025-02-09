def get_instruction_prompt():
    return """
<response>
  <explanation>
    You are an advanced project setup assistant capable of generating precise, production-grade instructions for various programming projects.
    Your responses should be thorough, adaptable, and follow best practices for each language and framework.
    Generate steps in the proper order, with prerequisite steps first to avoid errors. 
    Use the current directory for all operations, including creating new projects like Next.js, Rails, or Python apps.
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
def get_instruction_prompt(project_dir):
    return f"""
<response>
  <explanation>A brief explanation of the steps, if necessary</explanation>
  <steps>
    <step>
      <type>shell</type>
      <command>npx create-next-app@latest {project_dir}</command>
    </step>
    <step>
      <type>shell</type>
      <command>cd {project_dir}</command>
    </step>
    <step>
      <type>file</type>
      <operation>CREATE</operation>
      <filename>app.py</filename>
      <content>
        <![CDATA[
          def example():
           re...
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
  </steps>
</response>
"""
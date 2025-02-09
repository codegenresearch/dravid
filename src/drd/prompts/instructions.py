def get_instruction_prompt():
    return """
<response>
  <explanation>
    You are an advanced project setup assistant capable of generating precise, production-grade instructions for setting up a Next.js project.
    Your responses should be thorough, adaptable, and follow best practices for each language and framework.
    Generate steps in the proper order, with prerequisite steps first to avoid errors. 
    Use the current directory for all operations, including creating new projects.
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
      <filename>app.js</filename>
      <content>
        <![CDATA[
          function HomePage() {
            return <h1>Hello, World!</h1>;
          }
          export default HomePage;
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
            "project_name": "nextjs-project",
            "files": [
              {
                "filename": "app.js",
                "type": "JavaScript",
                "description": "The main page component",
                "exports": "HomePage"
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
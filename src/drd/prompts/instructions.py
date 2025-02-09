def get_instruction_prompt():
    return """
<response>
  <explanation>
    You are an advanced project setup assistant capable of generating precise, production-grade instructions for various programming projects.
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


### Addressing the Feedback:

1. **SyntaxError**: Removed any invalid syntax or comments that could cause a `SyntaxError`.
2. **Circular Imports**: Ensured that the code snippet does not introduce any circular imports. The function is self-contained and does not rely on external classes or functions that could cause circular dependencies.
3. **Explanation Section**: Simplified the explanation to focus on essential information.
4. **Command and File Operations**: Made the commands and file operations more generic and used relative paths.
5. **File Update Steps**: Provided only specific changes for file updates.
6. **Metadata Updates**: Included a step to update the dev server information in the project metadata.
7. **Requires Restart Tag**: Ensured the `<requires_restart>` tag is included and set to `true`.
8. **Avoid Destructive Commands**: Removed any destructive commands.
9. **Sequential Shell Commands**: Ensured each command is a separate step.
10. **File Creation and Updates**: Avoided including update steps for newly created files.
11. **Reusable Components**: Kept the code concise and under 120 lines.
12. **General Formatting**: Improved indentation and spacing for better readability.
def get_instruction_prompt():
    return """
<response>
  <explanation>
    You are an advanced project setup assistant capable of generating precise, production-grade instructions for various programming projects.
    Your responses should be thorough, adaptable, and follow best practices for each language and framework.
    Generate steps in the proper order, with prerequisite steps first to avoid errors. 
    Use the current directory for all operations, including creating new projects like Next.js, Rails, or Python apps.
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
      <operation>CREATE</operation>
      <filename>placeholder-image.png</filename>
      <content>
        <![CDATA[
        ]]>
      </content>
    </step>
    <step>
      <type>file</type>
      <operation>UPDATE</operation>
      <filename>drd.json</filename>
      <content>
        <![CDATA[
          + 1: {
          + 2:   "project_name": "pyser",
          + 3:   "files": [
          + 4:     {
          + 5:       "filename": "app.py",
          + 6:       "type": "Python",
          + 7:       "description": "...",
          + 8:       "exports": "None"
          + 9:     },
          +10:     {
          +11:       "filename": "drd.json",
          +12:       "type": "json",
          +13:       "description": "",
          +14:       "exports": "None"
          +15:     },
          +16:     {
          +17:       "filename": "placeholder-image.png",
          +18:       "type": "image",
          +19:       "description": "Placeholder image",
          +20:       "exports": "None"
          +21:     }
          +22:   ],
          +23:   "dev_server": {
          +24:     "start_command": "python start",
          +25:     "framework": "flask",
          +26:     "language": "python"
          +27:   }
          +28: }
        ]]>
      </content>
    </step>
    <step>
      <type>metadata</type>
      <operation>UPDATE_FILE</operation>
      <filename>drd.json</filename>
      <content>
        <![CDATA[
          + 1: {
          + 2:   "project_name": "pyser",
          + 3:   "files": [
          + 4:     {
          + 5:       "filename": "app.py",
          + 6:       "type": "Python",
          + 7:       "description": "...",
          + 8:       "exports": "None"
          + 9:     },
          +10:     {
          +11:       "filename": "drd.json",
          +12:       "type": "json",
          +13:       "description": "",
          +14:       "exports": "None"
          +15:     },
          +16:     {
          +17:       "filename": "placeholder-image.png",
          +18:       "type": "image",
          +19:       "description": "Placeholder image",
          +20:       "exports": "None"
          +21:     }
          +22:   ],
          +23:   "dev_server": {
          +24:     "start_command": "python start",
          +25:     "framework": "flask",
          +26:     "language": "python"
          +27:   }
          +28: }
        ]]>
      </content>
    </step>
  </steps>
</response>
"""


### Key Changes:
1. **Explanation**: Made the explanation more concise and relevant.
2. **XML Structure**: Ensured proper XML formatting with the `<response>` tag encapsulating the entire content.
3. **Step Order and Types**: Maintained logical step order and types.
4. **File Operations**: Used relative paths and precise line-by-line modifications for updates.
5. **Metadata Updates**: Included a step for updating metadata after creating or modifying files.
6. **Placeholder Files**: Used the naming convention for placeholder files.
7. **Requires Restart Tag**: Included the `<requires_restart>` tag with the correct value.
8. **Avoid Redundant Information**: Streamlined the steps to avoid redundancy.
9. **Follow Guidelines**: Adhered closely to the provided guidelines.
import click
from ...api.main import stream_dravid_api, call_dravid_vision_api
from ...utils.step_executor import Executor
from ...metadata.project_metadata import ProjectMetadataManager
from .dynamic_command_handler import handle_error_with_dravid, execute_commands
from ...utils import print_error, print_success, print_info, print_warning, run_with_loader
from ...utils.file_utils import get_file_content, fetch_project_guidelines
from .file_operations import get_files_to_modify
from ...utils.parser import parse_dravid_response


def execute_dravid_command(query, image_path, debug, instruction_prompt):
    print_info("Starting Dravid CLI tool..")
    print_warning("Ensure you are in a fresh directory or a git branch. Use Ctrl+C to exit.")

    executor = Executor()
    metadata_manager = ProjectMetadataManager(executor.current_dir)

    try:
        project_context = metadata_manager.get_project_context()

        if project_context:
            print_info("Identifying related files...")
            files_to_modify = run_with_loader(
                lambda: get_files_to_modify(query, project_context),
                "Analyzing project files"
            )

            print_info(f"Found {len(files_to_modify)} potentially relevant files.")
            if debug:
                for file in files_to_modify:
                    print(f"  - {file}")

            print_info("Reading file contents...")
            file_contents = {file: get_file_content(file) for file in files_to_modify if get_file_content(file)}
            for file in file_contents:
                print_info(f"  - Read content of {file}")

            project_guidelines = fetch_project_guidelines(executor.current_dir)
            file_context = "\n".join(
                [f"Current content of {file}:\n{content}" for file, content in file_contents.items()])
            full_query = f"{project_context}\n\nProject Guidelines:\n{project_guidelines}\n\nCurrent file contents:\n{file_context}\n\nUser query: {query}"
        else:
            print_info("No project context found. Creating a new project.")
            full_query = f"User query: {query}"

        print_info("Preparing to send query to Claude API...")
        if image_path:
            print_info(f"Processing image: {image_path}")
            commands = run_with_loader(
                lambda: call_dravid_vision_api(full_query, image_path, include_context=True, instruction_prompt=instruction_prompt),
                "Analyzing image and generating response"
            )
        else:
            print_info("Streaming response from Claude API...")
            xml_result = stream_dravid_api(full_query, include_context=True, instruction_prompt=instruction_prompt, print_chunk=False)
            commands = parse_dravid_response(xml_result)
            print_debug(commands)
            if debug:
                print_debug(f"Received {len(commands)} commands")

        if not commands:
            print_error("Failed to parse Claude's response or no commands to execute.")
            return

        print_info(f"Parsed {len(commands)} commands.")

        success, step_completed, error_message, all_outputs = execute_commands(
            commands, executor, metadata_manager, debug=debug)

        if not success:
            print_error(f"Failed to execute command at step {step_completed}. Error: {error_message}")
            print_info("Attempting to fix the error...")
            if handle_error_with_dravid(Exception(error_message), commands[step_completed-1], executor, metadata_manager, debug=debug):
                print_info("Fix applied successfully. Continuing with remaining commands.")
                remaining_commands = commands[step_completed:]
                success, _, error_message, additional_outputs = execute_commands(
                    remaining_commands, executor, metadata_manager, debug=debug)
                all_outputs += "\n" + additional_outputs
            else:
                print_error("Unable to fix the error. Skipping command and continuing.")

        print_info("Execution details:")
        click.echo(all_outputs)

        print_success("Dravid CLI tool execution completed.")
    except Exception as e:
        print_error(f"An unexpected error occurred: {str(e)}")
        if debug:
            import traceback
            traceback.print_exc()
import traceback
import click
from ...api.main import call_dravid_api
from ...utils import print_error, print_success, print_info, print_step, print_debug
from ...metadata.common_utils import generate_file_description
from ...prompts.error_resolution_prompt import get_error_resolution_prompt


def execute_commands(commands, executor, metadata_manager, is_fix=False, debug=False):
    """\n    Execute a list of commands using the provided executor and metadata manager.\n\n    :param commands: List of commands to execute.\n    :param executor: Executor instance to perform shell and file operations.\n    :param metadata_manager: Metadata manager to handle metadata operations.\n    :param is_fix: Boolean flag indicating if the commands are part of a fix.\n    :param debug: Boolean flag to enable debug mode.\n    :return: Tuple (success, total_steps, error_message, all_outputs).\n    """
    all_outputs = []
    total_steps = len(commands)

    for i, cmd in enumerate(commands, 1):
        step_description = "fix" if is_fix else "command"

        if cmd['type'] == 'explanation':
            output = f"Step {i}/{total_steps}: Explanation - {cmd['content']}"
            print_step(output)
        else:
            try:
                if cmd['type'] == 'shell':
                    output = handle_shell_command(cmd, executor)
                elif cmd['type'] == 'file':
                    output = handle_file_operation(cmd, executor, metadata_manager)
                elif cmd['type'] == 'metadata':
                    output = handle_metadata_operation(cmd, metadata_manager)
                elif cmd['type'] == 'requires_restart':
                    output = 'requires restart if the server is running'
                else:
                    raise ValueError(f"Unknown command type: {cmd['type']}")

                if isinstance(output, str) and output.startswith("Skipping"):
                    print_info(output)
                else:
                    output_message = f"Step {i}/{total_steps}: {cmd['type'].capitalize()} command - {cmd.get('command', '')} {cmd.get('operation', '')}\nOutput: {output}"
                    print_success(output_message)
                    output = output_message

                all_outputs.append(output)

            except Exception as e:
                error_message = f"Step {i}/{total_steps}: Error executing {step_description}: {cmd}\nError details: {str(e)}"
                print_error(error_message)
                all_outputs.append(error_message)
                return False, i, str(e), "\n".join(all_outputs)

        if debug:
            print_debug(f"Completed step {i}/{total_steps}")

    return True, total_steps, None, "\n".join(all_outputs)


def handle_shell_command(cmd, executor):
    """\n    Execute a shell command using the executor.\n\n    :param cmd: Command dictionary containing the command to execute.\n    :param executor: Executor instance to perform the command.\n    :return: Output of the command.\n    """
    output = executor.execute_shell_command(cmd['command'])
    if isinstance(output, str) and output.startswith("Skipping"):
        print_info(output)
        return output
    if output is None:
        raise Exception(f"Command failed: {cmd['command']}")
    print_success(f"Successfully executed: {cmd['command']}")
    if output:
        click.echo(f"Command output:\n{output}")
    return output


def handle_file_operation(cmd, executor, metadata_manager):
    """\n    Perform a file operation using the executor and update metadata if necessary.\n\n    :param cmd: Command dictionary containing the file operation details.\n    :param executor: Executor instance to perform the file operation.\n    :param metadata_manager: Metadata manager to update file metadata.\n    :return: Operation performed message.\n    """
    operation_performed = executor.perform_file_operation(
        cmd['operation'],
        cmd['filename'],
        cmd.get('content'),
        force=True
    )
    if isinstance(operation_performed, str) and operation_performed.startswith("Skipping"):
        print_info(operation_performed)
        return operation_performed
    elif operation_performed:
        print_success(f"Successfully performed {cmd['operation']} on file: {cmd['filename']}")
        update_file_metadata(cmd, metadata_manager, executor)
        return "Success"
    else:
        raise Exception(f"File operation failed: {cmd['operation']} on {cmd['filename']}")


def handle_metadata_operation(cmd, metadata_manager):
    """\n    Handle metadata operations.\n\n    :param cmd: Command dictionary containing the metadata operation details.\n    :param metadata_manager: Metadata manager to perform metadata operations.\n    :return: Metadata operation success message.\n    """
    if cmd['operation'] == 'UPDATE_FILE':
        if metadata_manager.update_metadata_from_file():
            print_success(f"Updated metadata for file: {cmd['filename']}")
            return f"Updated metadata for {cmd['filename']}"
        else:
            raise Exception(f"Failed to update metadata for file: {cmd['filename']}")
    else:
        raise Exception(f"Unknown operation: {cmd['operation']}")


def update_file_metadata(cmd, metadata_manager, executor):
    """\n    Update metadata for a file.\n\n    :param cmd: Command dictionary containing the file details.\n    :param metadata_manager: Metadata manager to update file metadata.\n    :param executor: Executor instance to get folder structure.\n    """
    project_context = metadata_manager.get_project_context()
    folder_structure = executor.get_folder_structure()
    file_type, description, exports = generate_file_description(
        cmd['filename'],
        cmd.get('content', ''),
        project_context,
        folder_structure
    )
    metadata_manager.update_file_metadata(
        cmd['filename'],
        file_type,
        cmd.get('content', ''),
        description,
        exports
    )
    print_info(f"Metadata updated for file: {cmd['filename']}")


def handle_error_with_dravid(error, cmd, executor, metadata_manager, depth=0, previous_context="", debug=False):
    """\n    Handle errors by sending them to Dravid for resolution and applying the suggested fixes.\n\n    :param error: Error encountered during command execution.\n    :param cmd: Command dictionary that caused the error.\n    :param executor: Executor instance to perform operations.\n    :param metadata_manager: Metadata manager to handle metadata operations.\n    :param depth: Depth of error handling recursion.\n    :param previous_context: Context of previous steps.\n    :param debug: Boolean flag to enable debug mode.\n    :return: Boolean indicating if the error was successfully resolved.\n    """
    if depth > 3:
        print_error("Max error handling depth reached. Unable to resolve the issue.")
        return False

    print_error(f"Error executing command: {error}")

    error_message = str(error)
    error_type = type(error).__name__
    error_trace = ''.join(traceback.format_exception(type(error), error, error.__traceback__))

    project_context = metadata_manager.get_project_context()
    error_query = get_error_resolution_prompt(
        previous_context, cmd, error_type, error_message, error_trace, project_context
    )

    print_info("🏏 Sending error information to Dravid for analysis (1 LLM call)...\n")

    try:
        fix_commands = call_dravid_api(error_query, include_context=True)
    except ValueError as e:
        print_error(f"Error parsing Dravid's response: {str(e)}")
        return False

    print_info("🩺 Dravid's suggested fix:", indent=2)
    print_info("🔨 Applying Dravid's suggested fix...", indent=2)

    fix_applied, step_completed, error_message, all_outputs = execute_commands(
        fix_commands, executor, metadata_manager, is_fix=True, debug=debug
    )

    if fix_applied:
        print_success("All fix steps successfully applied.")
        click.echo(all_outputs)
        return True
    else:
        print_error(f"Failed to apply the fix at step {step_completed}.")
        print_error(f"Error message: {error_message}")
        click.echo(all_outputs)

        return handle_error_with_dravid(
            Exception(error_message),
            {"type": "fix", "command": f"apply fix step {step_completed}"},
            executor,
            metadata_manager,
            depth + 1,
            all_outputs,
            debug
        )
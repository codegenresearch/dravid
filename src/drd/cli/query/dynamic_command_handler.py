import traceback
import click
from ...api.main import call_dravid_api
from ...utils import print_error, print_success, print_info, print_step, print_debug
from ...metadata.common_utils import generate_file_description
from ...prompts.error_resolution_prompt import get_error_resolution_prompt

# Importing necessary functions for handling different types of operations
from ...utils.step_executor import Executor
from ...utils.file_utils import get_file_content
from ...utils.input import confirm_with_user

def execute_commands(commands, executor, metadata_manager, is_fix=False, debug=False):
    """
    Executes a list of commands using the provided executor and metadata manager.
    
    :param commands: List of command dictionaries to execute.
    :param executor: Executor instance to perform shell and file operations.
    :param metadata_manager: MetadataManager instance to handle metadata operations.
    :param is_fix: Boolean indicating if the commands are part of a fix.
    :param debug: Boolean indicating if debug information should be printed.
    :return: Tuple of (success, total_steps, error_message, all_outputs).
    """
    all_outputs = []
    total_steps = len(commands)

    for i, cmd in enumerate(commands, 1):
        step_description = "fix" if is_fix else "command"

        if cmd['type'] == 'explanation':
            output = f"Step {i}/{total_steps}: Explanation - {cmd['content']}"
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
                    print_info(f"Step {i}/{total_steps}: {output}")
                else:
                    print_success(
                        f"Step {i}/{total_steps}: {cmd['type'].capitalize()} command - {cmd.get('command', '')} {cmd.get('operation', '')}\nOutput: {output}")

            except Exception as e:
                error_message = f"Step {i}/{total_steps}: Error executing {step_description}: {cmd}\nError details: {str(e)}"
                print_error(error_message)
                all_outputs.append(error_message)
                return False, i, str(e), "\n".join(all_outputs)

        all_outputs.append(output)
        if debug:
            print_debug(f"Completed step {i}/{total_steps}")

    return True, total_steps, None, "\n".join(all_outputs)


def handle_shell_command(cmd, executor):
    """
    Handles shell command execution.
    
    :param cmd: Command dictionary containing the shell command.
    :param executor: Executor instance to execute the shell command.
    :return: Output of the shell command.
    """
    output = executor.execute_shell_command(cmd['command'])
    if isinstance(output, str) and output.startswith("Skipping"):
        print_info(output)
        return output
    if output is None:
        raise Exception(f"Command failed: {cmd['command']}")
    if output:
        click.echo(f"Command output:\n{output}")
    return output


def handle_file_operation(cmd, executor, metadata_manager):
    """
    Handles file operations such as create, update, delete.
    
    :param cmd: Command dictionary containing the file operation details.
    :param executor: Executor instance to perform the file operation.
    :param metadata_manager: MetadataManager instance to update metadata if necessary.
    :return: Success message or raises an exception on failure.
    """
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
        print_success(
            f"Successfully performed {cmd['operation']} on file: {cmd['filename']}")
        return "Success"
    else:
        raise Exception(
            f"File operation failed: {cmd['operation']} on {cmd['filename']}")


def handle_metadata_operation(cmd, metadata_manager):
    """
    Handles metadata operations such as updating file metadata.
    
    :param cmd: Command dictionary containing the metadata operation details.
    :param metadata_manager: MetadataManager instance to perform the metadata operation.
    :return: Success message or raises an exception on failure.
    """
    if cmd['operation'] == 'UPDATE_FILE':
        if metadata_manager.update_metadata_from_file():
            print_success(f"Updated metadata for file: {cmd['filename']}")
            return f"Updated metadata for {cmd['filename']}"
        else:
            raise Exception(
                f"Failed to update metadata for file: {cmd['filename']}")
    else:
        raise Exception(f"Unknown operation: {cmd['operation']}")


def update_file_metadata(cmd, metadata_manager, executor):
    """
    Updates the metadata for a file based on its content and context.
    
    :param cmd: Command dictionary containing the file details.
    :param metadata_manager: MetadataManager instance to update the metadata.
    :param executor: Executor instance to retrieve project context and folder structure.
    """
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


def handle_error_with_dravid(error, cmd, executor, metadata_manager, depth=0, previous_context="", debug=False):
    """
    Handles errors by sending error information to Dravid for analysis and applying suggested fixes.
    
    :param error: Error object or message.
    :param cmd: Command dictionary that caused the error.
    :param executor: Executor instance to perform operations.
    :param metadata_manager: MetadataManager instance to handle metadata.
    :param depth: Current depth of error handling recursion.
    :param previous_context: Context of the previous error handling attempt.
    :param debug: Boolean indicating if debug information should be printed.
    :return: Boolean indicating if the error was successfully resolved.
    """
    if depth > 3:
        print_error(
            "Max error handling depth reached. Unable to resolve the issue.")
        return False

    print_error(f"Error executing command: {error}")

    error_message = str(error)
    error_type = type(error).__name__
    error_trace = ''.join(traceback.format_exception(
        type(error), error, error.__traceback__))

    project_context = metadata_manager.get_project_context()
    error_query = get_error_resolution_prompt(
        previous_context, cmd, error_type, error_message, error_trace, project_context
    )

    print_info(
        "🏏 Sending error information to Dravid for analysis (1 LLM call)...\n")

    try:
        fix_commands = call_dravid_api(
            error_query, include_context=True)
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
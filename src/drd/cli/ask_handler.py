import click
import sys
from ..api import stream_dravid_api, call_dravid_api_with_pagination
from ..utils.utils import print_error, print_info, print_warning
from ..metadata.project_metadata import ProjectMetadataManager
import os


def read_file_content(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        print_error(f"File not found: {file_path}. Please check the file path and try again.")
        return None


def suggest_file_alternative(file_path, project_metadata):
    print_info(f"Attempting to find an alternative for: {file_path}...")
    query = (
        f"The file '{file_path}' doesn't exist. Can you suggest similar existing files or interpret what the user might have meant? "
        f"Use the following project metadata as context:\n\n{project_metadata}"
    )
    response = call_dravid_api_with_pagination(query)
    print_info(f"Suggested alternative(s): {response}")
    return response


def handle_ask_command(ask, files, debug):
    print_header("Handling user query...")
    metadata_manager = ProjectMetadataManager(os.getcwd())
    project_metadata = metadata_manager.get_project_context()
    context = ""

    for file_path in files:
        content = read_file_content(file_path)
        if content is not None:
            context += f"Content of {file_path}:\n{content}\n\n"
        else:
            suggestion = suggest_file_alternative(file_path, project_metadata)
            user_input = click.prompt(
                "Do you want to proceed without this file? (y/n)", type=str, default='n'
            )
            if user_input.lower() != 'y':
                print_warning("Operation aborted by user.")
                return

    if ask:
        context += f"User question: {ask}\n"
    elif not sys.stdin.isatty():
        context += f"User question: {sys.stdin.read().strip()}\n"
    else:
        print_error("Please provide a question using --ask or through stdin.")
        return

    print_info("Sending query to Dravid AI...")
    print_info("LLM call to be made: 1")
    stream_dravid_api(context, print_chunk=True)
    print_success("Query processed successfully.")
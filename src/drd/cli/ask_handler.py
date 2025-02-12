import click
import sys
from ..api import stream_dravid_api, call_dravid_api_with_pagination
from ..utils.utils import print_error, print_info
from ..metadata.project_metadata import ProjectMetadataManager
import os


def read_file_content(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        print_error(f"File not found: {file_path}.")
        return None


def suggest_file_alternative(file_path, project_metadata):
    query = f"The file '{file_path}' doesn't exist. Can you suggest similar existing files or interpret what the user might have meant? Use the following project metadata as context:\n\n{project_metadata}"
    response = call_dravid_api_with_pagination(query, include_context=True)
    return response


def handle_ask_command(ask, file, debug):
    context = ""
    metadata_manager = ProjectMetadataManager(os.getcwd())
    project_metadata = metadata_manager.get_project_context()

    for file_path in file:
        content = read_file_content(file_path)
        if content is not None:
            context += f"Content of {file_path}:\n{content}\n\n"
        else:
            print_info("Finding similar or alternative file 🕵️‍♂️")
            print_info("Making LLM call: 1 🤖")
            suggestion = suggest_file_alternative(file_path, project_metadata)
            print_info(f"Suggestion: {suggestion}")
            user_input = click.prompt(
                "Do you want to proceed without this file? (y/n) [Confirm with y/n]", type=str)
            if user_input.lower() != 'y':
                print_error("Exiting without proceeding. ✋")
                return

    if ask:
        context += f"User question: {ask}\n"
    elif not sys.stdin.isatty():
        context += f"User question: {sys.stdin.read().strip()}\n"
    else:
        print_error("Please provide a question using --ask or through stdin 🔍")
        return

    print_info("Streaming response from LLM 🌐")
    stream_dravid_api(context, print_chunk=True)
    print_success("Dravid CLI Tool execution completed. ✅")
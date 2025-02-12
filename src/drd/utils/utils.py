import click
from colorama import Fore, Style, Back
import json
import os

METADATA_FILE = 'drd.json'

def print_error(message):
    click.echo(f"{Fore.RED}✘ Error: {message}{Style.RESET_ALL}")

def print_success(message):
    click.echo(f"{Fore.GREEN}✔ Success: {message}{Style.RESET_ALL}")

def print_info(message):
    click.echo(f"{Fore.YELLOW}ℹ Info: {message}{Style.RESET_ALL}")

def print_warning(message):
    click.echo(f"{Fore.YELLOW}⚠ Warning: {message}{Style.RESET_ALL}")

def print_debug(message):
    click.echo(click.style(f"DEBUG: {message}", fg="cyan"))

def print_step(step_number, total_steps, message):
    click.echo(
        f"{Fore.CYAN}[Step {step_number}/{total_steps}] {message}{Style.RESET_ALL}")

def create_confirmation_box(message, action):
    box_width = len(message) + 4
    box_top = f"╔{'═' * box_width}╗"
    box_bottom = f"╚{'═' * box_width}╝"
    box_content = f"║  {message}  ║"

    confirmation_box = f"""\n{Fore.YELLOW}{box_top}\n║  {Back.RED}{Fore.WHITE} CONFIRMATION REQUIRED {Style.RESET_ALL}{Fore.YELLOW}  ║\n{box_content}\n╠{'═' * box_width}╣\n║  Do you want to {action}?  ║\n{box_bottom}{Style.RESET_ALL}\n"""
    return confirmation_box

def print_command_details(commands):
    for index, cmd in enumerate(commands, start=1):
        cmd_type = cmd.get('type', 'Unknown')
        print_info(f"Command {index} - Type: {cmd_type}")

        if cmd_type == 'shell':
            command = cmd.get('command', 'N/A')
            print_info(f"  Shell Command: {command}")

        elif cmd_type == 'explanation':
            content = cmd.get('content', 'N/A')
            print_info(f"  Explanation: {content}")

        elif cmd_type == 'file':
            operation = cmd.get('operation', 'N/A')
            filename = cmd.get('filename', 'N/A')
            content_preview = cmd.get('content', 'N/A')
            if len(content_preview) > 50:
                content_preview = content_preview[:50] + "..."
            print_info(f"  File Operation: {operation}")
            print_info(f"  Filename: {filename}")
            print_info(f"  Content Preview: {content_preview}")

        elif cmd_type == 'metadata':
            operation = cmd.get('operation', 'N/A')
            print_info(f"  Metadata Operation: {operation}")
            if operation == 'UPDATE_DEV_SERVER':
                start_command = cmd.get('start_command', 'N/A')
                framework = cmd.get('framework', 'N/A')
                language = cmd.get('language', 'N/A')
                print_info(f"  Start Command: {start_command}")
                print_info(f"  Framework: {framework}")
                print_info(f"  Language: {language}")
            elif operation in ['UPDATE_FILE', 'UPDATE']:
                filename = cmd.get('filename', 'N/A')
                language = cmd.get('language', 'N/A')
                description = cmd.get('description', 'N/A')
                print_info(f"  Filename: {filename}")
                print_info(f"  Language: {language}")
                print_info(f"  Description: {description}")
        else:
            print_warning(f"  Unknown command type: {cmd_type}")
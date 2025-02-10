import click
from colorama import Fore, Style, Back
import json
import os
import shutil

METADATA_FILE = 'drd.json'


def print_header(message):
    terminal_width = shutil.get_terminal_size().columns
    header = f"{'=' * terminal_width}\n{message}\n{'=' * terminal_width}"
    click.echo(f"{Fore.CYAN}{header}{Style.RESET_ALL}")


def print_error(message):
    click.echo(f"{Fore.RED}✘ Error: {message}{Style.RESET_ALL}")


def print_success(message):
    click.echo(f"{Fore.GREEN}✔ Success: {message}{Style.RESET_ALL}")


def print_info(message, indent=0):
    click.echo(f"{' ' * indent}{Fore.YELLOW}ℹ Info: {message}{Style.RESET_ALL}")


def print_warning(message):
    click.echo(f"{Fore.YELLOW}⚠ Warning: {message}{Style.RESET_ALL}")


def print_debug(message):
    click.echo(click.style(f"DEBUG: {message}", fg="cyan"))


def print_step(step_number, total_steps, message):
    click.echo(
        f"{Fore.CYAN}[Step {step_number}/{total_steps}] {message}{Style.RESET_ALL}")


def create_confirmation_box(message, action):
    terminal_width = shutil.get_terminal_size().columns
    box_width = min(terminal_width - 4, len(message) + 4)
    box_top = f"╔{'═' * box_width}╗"
    box_bottom = f"╚{'═' * box_width}╝"
    box_content = f"║  {message.center(box_width - 2)}  ║"

    confirmation_box = f"""
{Fore.YELLOW}{box_top}
║  {Back.RED}{Fore.WHITE} CONFIRMATION REQUIRED {Style.RESET_ALL}{Fore.YELLOW}  ║
{box_content}
╠{'═' * box_width}╣
║  Do you want to {action}?  ║
{box_bottom}{Style.RESET_ALL}
"""
    return confirmation_box


def print_command_details(commands):
    for index, cmd in enumerate(commands, start=1):
        cmd_type = cmd.get('type', 'Unknown')
        print_info(f"Command {index} - Type: {cmd_type}", indent=2)

        if cmd_type == 'shell':
            print_info(f"  Command: {cmd.get('command', 'N/A')}", indent=4)

        elif cmd_type == 'explanation':
            print_info(f"  Explanation: {cmd.get('content', 'N/A')}", indent=4)

        elif cmd_type == 'file':
            operation = cmd.get('operation', 'N/A')
            filename = cmd.get('filename', 'N/A')
            content_preview = cmd.get('content', 'N/A')
            if len(content_preview) > 50:
                content_preview = content_preview[:50] + "..."
            print_info(f"  Operation: {operation}", indent=4)
            print_info(f"  Filename: {filename}", indent=4)
            print_info(f"  Content Preview: {content_preview}", indent=4)

        elif cmd_type == 'metadata':
            operation = cmd.get('operation', 'N/A')
            print_info(f"  Operation: {operation}", indent=4)
            if operation == 'UPDATE_DEV_SERVER':
                print_info(f"  Start Command: {cmd.get('start_command', 'N/A')}", indent=6)
                print_info(f"  Framework: {cmd.get('framework', 'N/A')}", indent=6)
                print_info(f"  Language: {cmd.get('language', 'N/A')}", indent=6)
            elif operation in ['UPDATE_FILE', 'UPDATE']:
                print_info(f"  Filename: {cmd.get('filename', 'N/A')}", indent=6)
                print_info(f"  Language: {cmd.get('language', 'N/A')}", indent=6)
                print_info(f"  Description: {cmd.get('description', 'N/A')}", indent=6)

        else:
            print_warning(f"  Unknown command type: {cmd_type}", indent=4)


### Changes Made:
1. **Added `print_header` Function**: This function dynamically adjusts the header size based on the terminal width.
2. **Improved `print_info` Function**: Added an `indent` parameter to allow for customizable indentation.
3. **Dynamic Confirmation Box**: Adjusted the `create_confirmation_box` function to dynamically adjust the box size based on the terminal width.
4. **Consistent Indentation**: Ensured consistent indentation in the `print_command_details` function for better readability.
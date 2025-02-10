import re
import click


def pretty_print_xml_stream(chunk, state):
    state['buffer'] += chunk

    max_iterations = 1000
    iteration_count = 0

    while iteration_count < max_iterations:
        iteration_count += 1

        if not state.get('in_step'):
            # Process explanation tags
            explanation_match = re.search(
                r'<\s*explanation\s*>(.*?)<\s*/\s*explanation\s*>',
                state['buffer'], re.DOTALL | re.IGNORECASE
            )
            if explanation_match:
                explanation = explanation_match.group(1).strip()
                click.echo(click.style("\nExplanation:", fg="green", bold=True), nl=False)
                click.echo(f" {explanation}")
                state['buffer'] = state['buffer'][explanation_match.end():]
                continue

            # Look for step start
            step_start_match = re.search(r'<\s*step\s*>', state['buffer'], re.IGNORECASE)
            if step_start_match:
                state['in_step'] = True
                state['buffer'] = state['buffer'][step_start_match.end():]
                continue

        if state['in_step']:
            step_end_match = re.search(r'<\s*/\s*step\s*>', state['buffer'], re.IGNORECASE)
            if step_end_match:
                step_content = state['buffer'][:step_end_match.start()]
                state['buffer'] = state['buffer'][step_end_match.end():]
                state['in_step'] = False

                # Process step content
                type_match = re.search(r'<\s*type\s*>(.*?)<\s*/\s*type\s*>', step_content, re.DOTALL | re.IGNORECASE)
                if type_match:
                    step_type = type_match.group(1).strip().lower()
                    if step_type == 'file':
                        operation_match = re.search(
                            r'<\s*operation\s*>(.*?)<\s*/\s*operation\s*>', step_content, re.DOTALL | re.IGNORECASE
                        )
                        filename_match = re.search(
                            r'<\s*filename\s*>(.*?)<\s*/\s*filename\s*>', step_content, re.DOTALL | re.IGNORECASE
                        )
                        if operation_match and filename_match:
                            operation = operation_match.group(1).strip()
                            filename = filename_match.group(1).strip()
                            click.echo(click.style("\nFile Operation:", fg="yellow", bold=True), nl=False)
                            click.echo(f" {operation} {filename}")

                        # Process CDATA content
                        cdata_start = step_content.find("<![CDATA[")
                        if cdata_start != -1:
                            cdata_end = step_content.rfind("]]>")
                            if cdata_end != -1:
                                cdata_content = step_content[cdata_start + 9:cdata_end]
                                click.echo(click.style("\nFile Content:", fg="cyan", bold=True))
                                click.echo(cdata_content)
                    elif step_type == 'shell':
                        command_match = re.search(
                            r'<\s*command\s*>(.*?)<\s*/\s*command\s*>', step_content, re.DOTALL | re.IGNORECASE
                        )
                        if command_match:
                            command = command_match.group(1).strip()
                            click.echo(click.style("\nShell Command:", fg="blue", bold=True), nl=False)
                            click.echo(f" {command}")
                continue

        # If we've reached this point, we couldn't process anything in this iteration
        break

    if iteration_count == max_iterations:
        click.secho("Warning: Maximum iterations reached, possible infinite loop detected.", fg="red", bold=True)


def stream_and_print_commands(chunks):
    state = {
        'buffer': '',
        'in_step': False,
    }

    for chunk in chunks:
        pretty_print_xml_stream(chunk, state)

    remaining_content = state['buffer'].strip()
    if remaining_content:
        click.echo(f"\nRemaining Content: {remaining_content}")

    click.echo()  # Final newline
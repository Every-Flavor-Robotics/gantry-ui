from typing import List, Optional, Tuple

from prompt_toolkit import HTML, PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style
from prompt_toolkit import print_formatted_text

from gantry_interface import GantryInterface

gantry = GantryInterface()

# Global command dictionary with command details and associated functions.
commands = {
    "set_waypoint": {
        "description": "<b>set_waypoint</b> [waypoint_index]",
        "help": "<b>set_waypoint</b> [waypoint_index]\n\tSets the desired waypoint to move to",
        "function": lambda args: set_waypoint(*args),
    },
    "set_pid_pos": {
        "description": "<b>set_pid</b> [P] [I] [D]",
        "help": "<b>set_pid</b> [P] [I] [D]\n\tSets the PID parameters with values [P], [I], and [D]",
        "function": lambda args: set_pid_parameters(*args),
    },
    "set_pid_vel": {
        "description": "<b>set_pid</b> [P] [I] [D]",
        "help": "<b>set_pid</b> [P] [I] [D]\n\tSets the PID parameters with values [P], [I], and [D]",
        "function": lambda args: set_pid_vel_parameters(*args),
    },
    "connect": {
        "description": "<b>connect</b> [ip] [port]",
        "help": "<b>connect</b> [ip] [port]\n\tConnects to the gantry at [ip]:[port]",
        "function": lambda args: gantry.connect(args[0], int(args[1])),
    },
    "help": {
        "description": "<b>help</b> [command]",
        "help": "<b>help</b> [command]\n\tPrints the help message for [command]",
        "function": lambda args: print_help(),
    },
    "quit": {
        "description": "<b>quit</b> [command]",
        "help": "<b>quit</b> [command]\n\tExits the application",
        "function": lambda args: False,
    },
}


def set_pid_parameters(p: str, i: str, d: str) -> bool:
    """
    Sets the PID parameters for the gantry using GantryInterface.

    Args:
        p (str): The P parameter.
        i (str): The I parameter.
        d (str): The D parameter.

    Returns:
        bool: True if successful, otherwise False.
    """
    global gantry

    try:
        # Convert the parameters to the appropriate data type (assuming float here)
        p_value, i_value, d_value = float(p), float(i), float(d)

        # Call the appropriate method in GantryInterface to set the PID parameters.
        # Assuming the GantryInterface has a method named 'set_pid'.
        gantry.set_pid_position_p_channel_0(p_value)
        gantry.set_pid_position_i_channel_0(i_value)
        gantry.set_pid_position_d_channel_0(d_value)

        print_formatted_text(
            HTML(
                f"<green>PID Parameters set to P: {p_value}, I: {i_value}, D: {d_value}</green>"
            )
        )
        return True
    except ValueError:
        print_formatted_text(HTML(f"<red>Invalid PID values provided.</red>"))
        return True


def set_pid_vel_parameters(p: str, i: str, d: str) -> bool:
    """
    Sets the PID parameters for the gantry using GantryInterface.

    Args:
        p (str): The P parameter.
        i (str): The I parameter.
        d (str): The D parameter.

    Returns:
        bool: True if successful, otherwise False.
    """
    global gantry

    try:
        # Convert the parameters to the appropriate data type (assuming float here)
        p_value, i_value, d_value = float(p), float(i), float(d)

        # Call the appropriate method in GantryInterface to set the PID parameters.
        # Assuming the GantryInterface has a method named 'set_pid'.
        gantry.set_pid_velocity_p_channel_0(p_value)
        gantry.set_pid_velocity_i_channel_0(i_value)
        gantry.set_pid_velocity_d_channel_0(d_value)

        print_formatted_text(
            HTML(
                f"<green>PID Parameters set to P: {p_value}, I: {i_value}, D: {d_value}</green>"
            )
        )
        return True
    except ValueError:
        print_formatted_text(HTML(f"<red>Invalid PID values provided.</red>"))
        return True


def set_waypoint(waypoint: str) -> bool:
    """
    Sets the waypoint for the gantry using GantryInterface.

    Args:
        waypoint (str): The waypoint index.

    Returns:
        bool: True if successful, otherwise False.
    """
    global gantry

    try:
        # Convert the parameters to the appropriate data type
        waypoint_index = int(waypoint)

        # Call the appropriate method in GantryInterface to set the PID parameters.
        # Assuming the GantryInterface has a method named 'set_pid'.
        gantry.set_target_waypoint(waypoint_index)

        print_formatted_text(HTML(f"<green>Waypoint set to {waypoint_index}</green>"))
        return True
    except ValueError:
        print_formatted_text(HTML(f"<red>Invalid waypoint provided.</red>"))
        return True


def execute_command(command: str, args: List[str]) -> Optional[bool]:
    """
    Executes the given command with the provided arguments.

    Args:
        command (str): The command to execute.
        args (List[str]): List of arguments for the command.

    Returns:
        Optional[bool]: Result of the command execution. If the result is False, the main loop will terminate.
    """
    global commands

    if command in commands:
        return commands[command]["function"](args)
    else:
        print_formatted_text(HTML(f"<red>Unknown command: {command}</red>"))
        return True


def print_help():
    """Prints the help messages for all the commands."""
    global commands

    for _, info in commands.items():
        print_formatted_text(HTML(info["help"]))


def main():
    """Main execution loop for the CLI application."""
    global commands, gantry

    print_formatted_text(
        HTML(
            "<green>Gantry Controller V0.0.1. Type help for a list of commands.</green>"
        )
    )
    custom_style = Style.from_dict({"": "#ffffff", "prompt": "#97c997"})

    # Initializing the PromptSession for interactive CLI.
    session = PromptSession(
        "gantry> ",
        style=custom_style,
        auto_suggest=AutoSuggestFromHistory(),
        completer=WordCompleter(list(commands.keys())),
        complete_while_typing=True,
    )

    while True:
        try:
            input_line = session.prompt()
            command, args = parse_command(input_line)

            # If the user just presses Enter without any command.
            if command is None:
                continue
            # Execute the command and exit the loop if the result is False.
            if not execute_command(command, args):
                gantry.disconnect()
                break
        except KeyboardInterrupt:  # Handles Ctrl-C.
            continue
        except EOFError:  # Handles Ctrl-D.
            gantry.disconnect()
            break


def parse_command(input_line: str) -> Tuple[Optional[str], List[str]]:
    """
    Parses the input line into a command and its arguments.

    Args:
        input_line (str): The raw input from the user.

    Returns:
        Tuple[Optional[str], List[str]]: Parsed command and its arguments.
    """
    if not input_line:
        return None, []

    split_line = input_line.split(" ")
    command = split_line[0]
    args = split_line[1:]

    return command, args


if __name__ == "__main__":
    main()

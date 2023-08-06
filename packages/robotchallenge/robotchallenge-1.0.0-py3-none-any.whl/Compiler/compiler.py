from robotchallenge.constants import COMMANDS
from robotchallenge.Commands.utlities import create_command
from robotchallenge.Commands.command import Command
import pathlib
from typing import List


class Compiler(object):
    """
    Compiler class.
    It converts a string into a list of instructions. That can be processed by the simulator. Input can be a file or a
    string where each instruction is seperated by end of line character.
    """

    def __init__(self, commands_string: str = None, file_path: str = None) -> None:
        """
        Initialize the compiler.
        :param commands_string:
        :param file_path:
        """
        self.instructions = []
        if file_path is not None:
            self.commands_string = pathlib.Path(file_path).read_text()
        else:
            self.commands_string = commands_string

    def compile(self) -> None:
        """
        Compile the commands string into a list of instructions.
        :return: None
        """

        for line in self.commands_string.split("\n"):
            tokens = line.replace(",", " ").split(" ")
            tokens = [x for x in tokens if x not in ["", [], None]]

            # ignore empty lines
            if not tokens:
                continue

            # ignr OUTPUT command line
            if tokens[0] == "Output:":
                continue

            if tokens[0] not in COMMANDS:
                raise CompilerError(f"Invalid Command: {tokens[0]}")

            if len(tokens) == 1:
                self.instructions.append(create_command(tokens[0]))
            else:
                self.instructions.append(create_command(tokens[0], *tokens[1:]))

    def get_instructions(self) -> List[Command]:
        """
        Get the compiled commands.
        :return: list of commands to be processed by the simulator
        """
        return self.instructions


class CompilerError(Exception):
    """
    CompilerError class.
    """

    def __init__(self, data: str):
        """
        Initialize the CompilerError class.
        :param data:
        """
        self.data = data

    def __str__(self)-> str:
        """
        Return the error message.
        :return: error msg as string
        """
        return repr(self.data)

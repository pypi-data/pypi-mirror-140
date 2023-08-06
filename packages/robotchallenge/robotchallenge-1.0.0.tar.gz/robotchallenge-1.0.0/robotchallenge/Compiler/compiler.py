from robotchallenge.Direction.direction import Direction
from robotchallenge.constants import ROTATE_DIRECTIONS
import pathlib


class Compiler(object):
    def __init__(self, commands_string=None, file_path=None):
        self.commands = []
        if file_path is not None:
            self.commands_string = pathlib.Path(file_path).read_text()
        else:
            self.commands_string = commands_string

    def compile(self):

        for command_string in self.commands_string.split("\n"):
            command = command_string.replace(",", " ").split(" ")
            command = [x for x in command if x not in ["", [], None]]

            if command[0] == "PLACE":
                command = {
                    'command': command[0],
                    'x_coordinate': int(command[1]),
                    'y_coordinate': int(command[2]),
                    'direction': Direction(command[3])
                }
            elif command[0] in ["MOVE"]:
                command = {
                    'command': command[0]
                }
            elif command[0] in ROTATE_DIRECTIONS:
                command = {
                    'command': "ROTATE",
                    'direction': Direction(command[0])
                }
            elif command[0] in ["REPORT"]:
                command = {
                    'command': command[0]
                }
            else:
                raise CompilerError(f"Invalid Command: {command[0]}")

            self.commands.append(command)

    def get_commands(self):
        return self.commands

    # def __str__(self):
    #     output_string = "Compiler(\n"
    #     for command in self.commands:
    #         output_string += "\t"+str(command) + "\n"
    #     output_string += ")"
    #     return output_string
    #
    # def __repr__(self):
    #     return self.__str__()


class CompilerError(Exception):
    def __init__(self, data):
        self.data = data

    def __str__(self):
        return repr(self.data)

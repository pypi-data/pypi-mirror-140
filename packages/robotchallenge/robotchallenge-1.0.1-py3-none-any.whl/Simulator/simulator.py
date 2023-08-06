import logging
from robotchallenge.Board.board import Board
from robotchallenge.Robot.robot import Robot
from robotchallenge.Commands.command import Command
from robotchallenge.constants import ROTATE_DIRECTIONS
from typing import List
from robotchallenge.Simulator.utilities import get_output_string

class Simulator:
    """
    Simulator class.
    It is responsible for the simulation of the robot on the board. It processes each commond and updates state of the robot.
    And it also returns the state of the robot.
    """

    def __init__(self, board: Board, robot: Robot, commands: List[Command]) -> None:
        self.board = board
        self.robot = robot
        self.commands = commands

    def __str__(self) -> str:
        """
        Returns the string representation of the simulator.
        :return:
        """
        return "Simulator(board={}, robot={}, commands={})".format(self.board, self.robot, self.commands)

    def run(self) -> None:
        """
        Runs the simulator.
        :return: None
        """
        for command in self.commands:
            if command.get_command() == "PLACE":
                if self.board.position_on_board(command.get_argument("x_coordinate"),
                                                command.get_argument("y_coordinate")):
                    self.robot.place(command.get_argument("x_coordinate"), command.get_argument("y_coordinate"),
                                     command.get_argument("direction"))
            elif command.get_command() == "MOVE":
                if self.robot.is_placed:
                    x_coordinate, y_coordinate = self.robot.future_position()
                    if self.board.position_on_board(x_coordinate, y_coordinate):
                        self.robot.move()
            elif command.get_command() in ROTATE_DIRECTIONS:
                if self.robot.is_placed:
                    self.robot.rotate(command.get_command())
            elif command.get_command() == "REPORT":
                if self.robot.is_placed:
                    print(self.get_result())
            else:
                SimulatorError("Invalid command: {}".format(command.get_command()))
            logging.debug(command)
            logging.debug(self.robot)

    def get_result(self) -> str:
        """
        Returns the result of the simulator.
        :return: string representation of the output of the simulator.
        """
        return get_output_string(self.robot.x_coordinate, self.robot.y_coordinate, self.robot.direction_facing)


class SimulatorError(Exception):
    """
    SimulatorError class.
    It is responsible for raising the error when the simulator is not able to process the command.
    """
    def __init__(self, data):
        self.data = data

    def __str__(self):
        return repr(self.data)


class Simulator:
    def __init__(self, board, robot, commands):
        self.board = board
        self.robot = robot
        self.commands = commands

    def __str__(self):
        return "Simulator(board={}, robot={}, commands={})".format(self.board, self.robot, self.commands)

    def run(self):
        for command in self.commands:
            if command["command"] == "PLACE":
                if self.board.position_on_board(command["x_coordinate"], command["y_coordinate"]):
                    self.robot.place(command["x_coordinate"], command["y_coordinate"], command["direction"])
            elif command["command"] == "MOVE":
                if self.robot.is_placed:
                    x_coordinate, y_coordinate = self.robot.future_position()
                    if self.board.position_on_board(x_coordinate, y_coordinate):
                        self.robot.move()
            elif command["command"] == "ROTATE":
                if self.robot.is_placed:
                    self.robot.change_direction(command["direction"])
            elif command["command"] == "REPORT":
                if self.robot.is_placed:
                    print(self.get_result())
            else:
                SimulatorError("Invalid command: {}".format(command["command"]))

    def get_result(self):
        return "Output: {},{},{}".format(
            self.robot.x_coordinate,
            self.robot.y_coordinate,
            self.robot.direction_facing.direction
        )


class SimulatorError(Exception):
    def __init__(self, data):
        self.data = data

    def __str__(self):
        return repr(self.data)

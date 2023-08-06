from robotchallenge.constants import ROTATE_DIRECTIONS, DIRECTIONS
from robotchallenge.constants import DIRECTION_STEP_MAPPING, DIRECTION_ROTATION_MAPPING


class Robot:
    """
    Robot class
    It stores the current position and direction of the robot
    It also has methods to move the robot and rotate it
    It also has a method to get the next position of the robot
    """

    def __init__(self, x_coordinate: int, y_coordinate: int, direction_facing: str) -> None:
        """
        Initialize the robot
        :param x_coordinate: x coordinate of the robot
        :param y_coordinate: y coordinate of the robot
        :param direction_facing: direction the robot is facing
        """
        self.direction_facing = None
        self.y_coordinate = None
        self.x_coordinate = None
        self.is_placed = False
        self.set_x_coordinate(x_coordinate)
        self.set_y_coordinate(y_coordinate)
        self.set_direction_facing(direction_facing)

    def set_x_coordinate(self, x_coordinate: int) -> None:
        """
        Set the x coordinate of the robot
        :param x_coordinate: x coordinate of the robot
        :return: None
        """
        if not isinstance(x_coordinate, int):
            raise RobotTypeError('Invalid x_coordinate: {}'.format(x_coordinate))
        self.x_coordinate = x_coordinate

    def set_y_coordinate(self, y_coordinate: int) -> None:
        """
        Set the y coordinate of the robot
        :param y_coordinate: y coordinate of the robot
        :return: None
        """
        if not isinstance(y_coordinate, int):
            raise RobotTypeError('Invalid y_coordinate: {}'.format(y_coordinate))
        self.y_coordinate = y_coordinate

    def set_direction_facing(self, direction: str) -> None:
        """
        Set the direction the robot is facing
        :param direction: direction the robot is facing
        :return: None
        """
        if not isinstance(direction, str):
            raise RobotTypeError('Invalid direction_facing: {}'.format(direction))
        if direction not in DIRECTIONS:
            raise RobotTypeError('Invalid direction: {}'.format(direction))
        self.direction_facing = direction

    def rotate(self, rotation_direction: str) -> None:
        """
        Rotate the robot
        :param rotation_direction: rotation direction
        :return: None
        """
        if rotation_direction not in ROTATE_DIRECTIONS:
            raise RobotTypeError('Invalid direction: {}'.format(rotation_direction))
        self.direction_facing = DIRECTION_ROTATION_MAPPING[self.direction_facing][rotation_direction]

    def place(self, x_coordinate: int, y_coordinate: int, direction_facing: str) -> None:
        """
        Place the robot
        :param x_coordinate: x coordinate of the robot
        :param y_coordinate: y coordinate of the robot
        :param direction_facing: direction the robot is facing
        :return: None
        """
        self.is_placed = True
        self.set_x_coordinate(x_coordinate)
        self.set_y_coordinate(y_coordinate)
        self.set_direction_facing(direction_facing)

    def move(self) -> None:
        """
        Move the robot. Update the x and y coordinates by moving the direction the robot is facing
        :return: None
        """
        self.x_coordinate = self.x_coordinate + DIRECTION_STEP_MAPPING[self.direction_facing][0]
        self.y_coordinate = self.y_coordinate + DIRECTION_STEP_MAPPING[self.direction_facing][1]

    def future_position(self) -> tuple:
        """
        Get the next position of the robot if the robot moves in the direction it is facing
        :return:
        """
        return self.x_coordinate + DIRECTION_STEP_MAPPING[self.direction_facing][0], \
               self.y_coordinate + DIRECTION_STEP_MAPPING[self.direction_facing][1]

    def __str__(self) -> str:
        """
        Return the string representation of the robot
        :return: robot string
        """
        return "Robot(x_coordinate={}, y_coordinate={}, direction_facing={}, is_placed={})".format(
            self.x_coordinate, self.y_coordinate, self.direction_facing, self.is_placed
        )

    def __repr__(self)-> str:
        """
        Return the string representation of the robot
        :return: robot string
        """
        return self.__str__()


class RobotTypeError(Exception):
    """
    Exception class for Robot
    """
    def __init__(self, data):
        self.data = data

    def __str__(self):
        return repr(self.data)

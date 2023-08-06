from robotchallenge.constants import ROTATE_DIRECTIONS, DIRECTIONS
from robotchallenge.constants import DIRECTION_STEP_MAPPING, DIRECTION_ROTATION_MAPPING


class Robot:
    def __init__(self, x_coordinate, y_coordinate, direction_facing):
        self.direction_facing = None
        self.y_coordinate = None
        self.x_coordinate = None
        self.is_placed = False
        self.set_x_coordinate(x_coordinate)
        self.set_y_coordinate(y_coordinate)
        self.set_direction_facing(direction_facing)

    def set_x_coordinate(self, x_coordinate):
        if not isinstance(x_coordinate, int):
            raise RobotTypeError('Invalid x_coordinate: {}'.format(x_coordinate))
        self.x_coordinate = x_coordinate

    def set_y_coordinate(self, y_coordinate):
        if not isinstance(y_coordinate, int):
            raise RobotTypeError('Invalid y_coordinate: {}'.format(y_coordinate))
        self.y_coordinate = y_coordinate

    def set_direction_facing(self, direction):
        if not isinstance(direction, str):
            raise RobotTypeError('Invalid direction_facing: {}'.format(direction))
        if direction not in DIRECTIONS:
            raise RobotTypeError('Invalid direction: {}'.format(direction))
        self.direction_facing = direction

    def rotate(self, rotation_direction):
        if rotation_direction not in ROTATE_DIRECTIONS:
            raise RobotTypeError('Invalid direction: {}'.format(rotation_direction))
        self.direction_facing = DIRECTION_ROTATION_MAPPING[self.direction_facing][rotation_direction]

    def place(self, x_coordinate, y_coordinate, direction_facing):
        self.is_placed = True
        self.set_x_coordinate(x_coordinate)
        self.set_y_coordinate(y_coordinate)
        self.set_direction_facing(direction_facing)

    def move(self):
        self.x_coordinate = self.x_coordinate + DIRECTION_STEP_MAPPING[self.direction_facing][0]
        self.y_coordinate = self.y_coordinate + DIRECTION_STEP_MAPPING[self.direction_facing][1]

    def future_position(self):
        return self.x_coordinate + DIRECTION_STEP_MAPPING[self.direction_facing][0], \
               self.y_coordinate + DIRECTION_STEP_MAPPING[self.direction_facing][1]

    def __str__(self):
        return "Robot(x_coordinate={}, y_coordinate={}, direction_facing={}, is_placed={})".format(
            self.x_coordinate, self.y_coordinate, self.direction_facing, self.is_placed
        )

    def __repr__(self):
        return self.__str__()


class RobotTypeError(Exception):
    def __init__(self, data):
        self.data = data

    def __str__(self):
        return repr(self.data)

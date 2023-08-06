from robotchallenge.Direction.direction import Direction, ROTATE_DIRECTIONS
from robotchallenge.constants import DIRECTION_STEP_MAPPING, DIRECTION_ROTATION_MAPPING


class Robot:
    def __init__(self, x_coordinate, y_coordinate, direction_facing):
        self.x_coordinate = x_coordinate
        self.y_coordinate = y_coordinate
        self.direction_facing = Direction(direction_facing)
        self.is_placed = False

    def place(self, x_coordinate, y_coordinate, direction_facing):
        self.is_placed = True
        self.x_coordinate = x_coordinate
        self.y_coordinate = y_coordinate
        self.direction_facing = Direction(direction_facing)

    def move(self):
        self.x_coordinate = self.x_coordinate + DIRECTION_STEP_MAPPING[self.direction_facing.direction][0]
        self.y_coordinate = self.y_coordinate + DIRECTION_STEP_MAPPING[self.direction_facing.direction][1]

    def change_direction(self, direction):
        if direction not in ROTATE_DIRECTIONS:
            raise RobotTypeError('Invalid direction: {}'.format(direction))

        self.direction_facing = Direction(DIRECTION_ROTATION_MAPPING[self.direction_facing.direction][direction])

    def future_position(self):
        return self.x_coordinate + DIRECTION_STEP_MAPPING[self.direction_facing.direction][0], \
               self.y_coordinate + DIRECTION_STEP_MAPPING[self.direction_facing.direction][1]

    def __str__(self):
        return "Robot(x_coordinate={}, y_coordinate={}, direction_facing={})".format(
            self.x_coordinate, self.y_coordinate, self.direction_facing
        )

    def __repr__(self):
        return self.__str__()


class RobotTypeError(Exception):
    def __init__(self, data):
        self.data = data

    def __str__(self):
        return repr(self.data)

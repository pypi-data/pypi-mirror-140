from robotchallenge.constants import DIRECTIONS, ROTATE_DIRECTIONS


class Direction:
    def __init__(self, direction):

        self.direction = "NONE"
        if direction not in DIRECTIONS and direction not in ROTATE_DIRECTIONS:
            raise DirectionError("Invalid direction")
        else:
            self.direction = direction

    def __eq__(self, direction=None):
        """Overrides the default implementation"""
        return self.direction == direction if isinstance(direction, str) else False

    def __ne__(self, direction=None):
        """Overrides the default implementation"""
        return self.direction == direction if isinstance(direction, str) else False

    def __str__(self):
        return str(self.direction)

    def __repr__(self):
        return f"Direction(direction='{self.direction}')"

    def __hash__(self):
        return hash(self.direction)


class DirectionError(Exception):
    def __init__(self, data):
        self.data = data

    def __str__(self):
        return repr(self.data)

class Board:
    # Constructor
    def __init__(self, size):
        self.x_min = 0
        self.x_max = size - 1
        self.y_min = 0
        self.y_max = size - 1

    def position_on_board(self, x_coordinate, y_coordinate):
        # return True if position is on board
        # return False if position is not on board
        return (
                self.x_min <= x_coordinate <= self.x_max
                and self.y_min <= y_coordinate <= self.y_max
        )

    def __str__(self):
        return "Board(x_min={}, x_max={}, y_min={}, y_max={})".format(
                self.x_min, self.x_max, self.y_min, self.y_max
        )

    def __repr__(self):
        return self.__str__()


class BoardTypeError(Exception):
    def __init__(self, data):
        self.data = data

    def __str__(self):
        return repr(self.data)

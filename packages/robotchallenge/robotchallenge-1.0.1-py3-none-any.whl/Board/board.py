class Board:
    """
    Board class.
    - It holds the constraints on space the robot can travel
    - It informs if a future move will be valid or not
    """

    # Constructor
    def __init__(self, size: int) -> None:
        self.x_min = 0  # x_min is always 0
        self.x_max = size - 1  # x_max is always size - 1
        self.y_min = 0  # y_min is always 0
        self.y_max = size - 1  # y_max is always size - 1

    def position_on_board(self, x_coordinate: int, y_coordinate: int) -> bool:
        """
        Check if the position is on the board
        :param x_coordinate: an integer representing the x coordinate
        :param y_coordinate: an integer representing the y coordinate
        :return: "True" if the position is on the board, "False" otherwise
        """
        # return True if position is on board
        # return False if position is not on board
        return (
                self.x_min <= x_coordinate <= self.x_max
                and self.y_min <= y_coordinate <= self.y_max
        )

    def __str__(self) -> str:
        """
        String representation of the board
        :return: String representing the board
        """
        return "Board(x_min={}, x_max={}, y_min={}, y_max={})".format(
            self.x_min, self.x_max, self.y_min, self.y_max
        )

    def __repr__(self):
        """
        String representation of the board
        :return: String representing the board
        """
        return self.__str__()


class BoardTypeError(Exception):
    """
    Exception raised when the type of the board is not valid
    """
    def __init__(self, data):
        self.data = data

    def __str__(self):
        return repr(self.data)

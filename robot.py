from cell import Cell
from color import Color
from rotation import Rotation


class Robot:
    def __init__(self):
        # the cell where to robot starts
        # doesnt really matter, since all other coordinates
        # are relativ to this position
        self.start_cell = Cell(0, 0)

        # the cell that will be extended upon moving into a direction
        # similar to the behaviour of a linked list
        # first value is cell, second value is distance from origin(0, 0) to this cell
        self.current_cell = (self.start_cell, 0.0)

        # the current rotation of the robot
        # that will be used in the move() method
        self.current_rotation = Rotation.UP

        # the knowledge base of the robot
        # will be used for checking wether
        # a position has already been visited
        # allows for circular paths
        self.lookup = {}
        self.lookup.append(self.current_cell[0])

    def rotate_left(self) -> None:
        match self.current_rotation:
            case Rotation.UP:
                self.current_rotation = Rotation.LEFT
            case Rotation.DOWN:
                self.current_rotation = Rotation.RIGHT
            case Rotation.LEFT:
                self.current_rotation = Rotation.DOWN
            case Rotation.RIGHT:
                self.current_rotation = Rotation.UP

    def detect_color(self) -> Color:
        # TODO: get color via light sensor
        return Color.WHITE

    def rotate_right(self) -> None:
        match self.current_rotation:
            case Rotation.UP:
                self.current_rotation = Rotation.RIGHT
            case Rotation.DOWN:
                self.current_rotation = Rotation.LEFT
            case Rotation.LEFT:
                self.current_rotation = Rotation.UP
            case Rotation.RIGHT:
                self.current_rotation = Rotation.DOWN

    def graph_lookup(self, x, y) -> Cell:
        for entry in self.lookup:
            if entry.x == x and entry.y == y:
                return entry
        return None

    def detect(self):
        # rotate 360 degrees
        # and check for possible neighbors in existing knowledge base
        left = self.graph_lookup(self.x - 1, self.y)
        right = self.graph_lookup(self.x + 1, self.y)
        up = self.graph_lookup(self.x, self.y + 1)
        down = self.graph_lookup(self.x, self.y - 1)

        # assign neighbors found in knowledge base
        # or create a new neighbour
        self.current_cell.left = left or Cell(self.x - 1, self.y)
        self.current_cell.right = right or Cell(self.x + 1, self.y)
        self.current_cell.up = up or Cell(self.x, self.y + 1)
        self.current_cell.down = down or Cell(self.x, self.y - 1)

    def move(self) -> None:
        previous, previous_origin = self.current_cell
        next_cell = Cell(previous.x, previous.y)
        if self.current_rotation == Rotation.UP:
            next_cell.y += 1
            self.current_cell.up = next_cell
        if self.current_rotation == Rotation.DOWN:
            next_cell.y -= 1
            self.current_cell.down = next_cell
        if self.current_rotation == Rotation.RIGHT:
            next_cell.x += 1
            self.current_cell.right = next_cell
        if self.current_rotation == Rotation.LEFT:
            next_cell.x -= 1
            self.current_cell.left = next_cell

        # TODO: validate if adjacent cells are being set correctly
        lookup = self.graph_lookup(next_cell.x, next_cell.y) or next_cell
        # TODO: assertions
        self.current_cell = next_cell
        self.current_cell.color = self.detect_color

from color import Color


class Cell():
    def __init__(self):
        self.x = 0
        self.y = 0

        self.left = None
        self.right = None
        self.up = None
        self.down = None
        self.color = Color.WHITE

from psychopy import visual, clock

# Specify coordinates in a user-friendly x and y object
class Coordinate:
    x = 0
    y = 0

    def __init__(self, x, y):
        self.x = x
        self.y = y

# Create a grid by specifying rectangles to be repeated
class Grid:
    start = Coordinate(0, 0)
    width = 1
    height = 1

    def __init__(self, width_in_cells, height_in_cells, psychopy_rect, start_coordinates):
        # we would copy this stuff across, but here we do some shorthand hacks
        self.width = width_in_cells
        self.height = height_in_cells
        self.rect = psychopy_rect
        self.start = start_coordinates

# Psychopy output window
win = visual.Window(
    size=[800, 800],
    units="pix",
    fullscr=False,
    color=[1, 1, 1]
)

win.mouseVisible = True

# Using our grid class to define a grid
grid = Grid(
    width_in_cells=3,
    height_in_cells=3,
    # including the rectangles we'll be using as cells
    psychopy_rect=visual.Rect(
        win=win,
        units="pix",
        width=50,
        height=50,
        fillColor=[1, -1, -1],
        lineColor=[-1, -1, 1]
    ),
    start_coordinates=Coordinate(0, 0)
)

# Iterate through the cells to draw them in the appropriate places
for r in range(grid.width):
    for c in range(grid.height):
        # Set grid cell position properties
        rect = grid.rect
        rect.pos = (
            grid.start.x + (r - 1) * grid.rect.width,
            grid.start.y + (c - 1) * grid.rect.height
        )

        rect.draw()


# Draw the grid to the screen
win.flip()
clock.wait(2)

from psychopy import visual, clock
from math import floor, ceil

# Specify coordinates in a user-friendly x and y object
class Coordinate:
    x = 0
    y = 0

    def __init__(self, x, y):
        self.x = x
        self.y = y

# Create a grid by specifying rectangles to be repeated
class Grid:

    def __init__(self, width_in_cells, height_in_cells, psychopy_rect, start_coordinates):
        # we would copy this stuff across, but here we do some shorthand hacks
        self.width = width_in_cells
        self.height = height_in_cells
        self.rect = psychopy_rect
        # bump the start coordinates to account for rectangles drawing centred on their start points
        start_coordinates.x += ceil(self.rect.width / 2)
        start_coordinates.y += ceil(self.rect.height / 2)
        self.start = start_coordinates

    # Return the pixel offset of the cell at coordinates r, c
    def coordToPixelOffset(self, r, c):
        return (
            grid.start.x + (r * grid.rect.width),
            grid.start.y + (c * grid.rect.height)
        )

# Adjust text output by -half a character in the x direction
halfCharPx = 10

# Psychopy output window
win = visual.Window(
    size=[1000, 800],
    units="pix",
    fullscr=False,
    color=[1, 1, 1]
)

win.mouseVisible = True

# Using our grid class to define a grid
grid = Grid(
    width_in_cells=5,
    height_in_cells=5,
    # including the rectangles we'll be using as cells
    psychopy_rect=visual.Rect(
        win=win,
        width=50,
        height=50,
        fillColor=[1, 1, 1],
        lineColor=[-1, -1, -1]
    ),
    start_coordinates=Coordinate(-(win.size[0] / 2)+100, -(win.size[1] / 2)+300)
)

# Iterate through the cells to draw them in the appropriate places
def make_grid(grid):
    for r in range(grid.width):
        for c in range(grid.height):
            # Set grid cell position properties
            rect = grid.rect
            rect.pos = grid.coordToPixelOffset(r, c)

            rect.draw()

# Draw stimulus
coords = grid.coordToPixelOffset(2, 4)
coords = (coords[0] - halfCharPx, coords[1])

stim = visual.TextStim(
    win=win,
    font='monospace',
    text='4',
    pos=coords,
    color=[-1, -1, 1],
    # autoDraw=True,
    wrapWidth=1  # no idea why we need this, but apparently we do. Complaints to PsychoPy :)
)

make_grid(grid)
win.flip()
clock.wait(2)


make_grid(grid)
stim.draw()
win.flip()
clock.wait(2)
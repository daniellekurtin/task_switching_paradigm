import numpy as np
from psychopy import visual, clock, event
from math import floor, ceil
from random import randint, shuffle
from datetime import datetime

# The Experiment class simply holds values which must remain constant throughout the experiment.
# The values it holds are ones we define at creation time.
# Maybe later we'll add some default values to give an idea of how it should be used.
# Expects:
# trials {Trial[]} list of trials to run
class Experiment:
    def __init__(self, **kwargs):
        for k in kwargs.keys():
            self.__setattr__(k, kwargs[k])

        for t in self.trials:
            t.experiment = self

    def run(self):
        for t in self.trials:
            t.run()


# Any set of screens in the experiment is a component. These could be trials, instructions, breaks, etc.
class Component:
    def __init__(self, **kwargs):
        self.logEntries = []

        for k in kwargs.keys():
            self.__setattr__(k, kwargs[k])

    # Write a log entry for this component
    # entry {string} text to enter into the log
    # level {string} notification level of entry
    def log(self, entry, level = 'INFO'):
        self.logEntries.append(str(datetime.now()) + ': ' + level + ' - ' + entry)


# Any values which might vary from trial to trial are recorded in a Trial
# Trials expect:
# win {psychopy Window object}
class Trial(Component):
    def __init__(self, win, **kwargs):
        super().__init__(**kwargs)
        self.win = win
        self.win.mouseVisible = True

        self.grid = Grid(
            width_in_cells=4,
            height_in_cells=4,
            # including the rectangles we'll be using as cells
            psychopy_rect=visual.Rect(
                win=win,
                width=50,
                height=50,
                fillColor=[1, 1, 1],
                lineColor=[-1, -1, -1]
            ),
            start_pos_tuple=(-(win.size[0] / 2), -(win.size[1] / 2))
        )

        for k in kwargs.keys():
            self.__setattr__(k, kwargs[k])


    def drawStim(self, stimulus, grid = None):
        if grid is None:
            grid = self.grid

        dim = stimulus.shape
        for r in range(dim[0]):
            for c in range(dim[1]):
                if stimulus[r, c] is not None:
                    # nudge the x coordinate of the stimulus to centre it in the box
                    coords = grid.coordToPixelOffset(r, c)
                    coords = (coords[0] - halfCharPx, coords[1])

                    stim = visual.TextStim(
                        text=stimulus[r, c],
                        win=win,
                        font='monospace',
                        pos=coords,
                        color=[-1, -1, 1],
                        wrapWidth=1  # no idea why we need this, but apparently we do. Complaints to PsychoPy :)
                    )
                    stim.draw()

    def run(self):
        # Run the whole trial, including collecting data
        pass


# Expects:
# stimulus {int[]} digits to display sequentially
# stimulusDuration {float} seconds to display each digit
class TrialDigitSpan(Trial):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def run(self):
        self.prepare()
        self.showStimulus()
        self.collectResponse()

    def prepare(self):
        self.win.flip()
        clock.wait(.5)
        pass

    def showStimulus(self):
        for n in self.stimulus:
            self.drawNumber(n)
            clock.wait(self.stimulusDuration)

            self.grid.draw()
            self.win.flip()
            clock.wait(.5)

    def collectResponse(self):
        # PsychoPy click response stuff?
        self.drawAnswerGrids()
        self.win.flip()

        clock.wait(1)

        response = self.getMouseInput()
        self.log('Mouse position = ' + str(response["position"]))

    def drawNumber(self, n):
        self.grid.draw()
        self.drawStim(n)
        self.win.flip()

    def drawAnswerGrids(self):
        for i in range(len(self.answers)):
            g = Grid(
                width_in_cells=4,
                height_in_cells=4,
                # including the rectangles we'll be using as cells
                psychopy_rect=visual.Rect(
                    win=win,
                    width=25,
                    height=25,
                    fillColor=[1, 1, 1],
                    lineColor=[-1, -1, -1]
                ),
                start_pos_tuple=(
                    win.size[0] / 2 - 25 * (4 + 1),
                    win.size[1] / 2 - 25 * (4 + 1) - win.size[1] * i / 3
                )
            )
            g.draw()

            # Draw the puported answer over this grid
            self.drawStim(self.answers[i], grid=g)

    def getMouseInput(self):
        event.clearEvents()  # get rid of other, unprocessed events
        buttons, times = myMouse.getPressed(getTime=True)
        while buttons == [0, 0, 0]:
            buttons, times = myMouse.getPressed(getTime=True)
            if buttons[0]:
                break

            times = myMouse.clickReset()
            pos = myMouse.getPos()
        return {
            "time": times,
            "position": pos
        }

class TrialSpatialSpan(Trial):
    def __init__(self, **kwargs):
        super().__init__(kwargs)


class TrialSpatialRotation(Trial):
    def __init__(self, **kwargs):
        super().__init__(kwargs)


class TrialRest(Trial):
    def __init__(self, **kwargs):
        super().__init__(kwargs)


# Create a grid by specifying rectangles to be repeated
class Grid:

    def __init__(self, width_in_cells, height_in_cells, psychopy_rect, start_pos_tuple):
        # we would copy this stuff across, but here we do some shorthand hacks
        self.width = width_in_cells
        self.height = height_in_cells
        self.rect = psychopy_rect
        # bump the start coordinates to account for rectangles drawing centred on their start points
        self.start = (start_pos_tuple[0] + ceil(self.rect.width / 2),
                      start_pos_tuple[1] + ceil(self.rect.height / 2))

    # Return the pixel offset of the cell at coordinates r, c
    def coordToPixelOffset(self, r, c):
        return (
            self.start[0] + (r * self.rect.width),
            self.start[1] + (c * self.rect.height)
        )

    def draw(self):
        # Iterate through the cells to draw them in the appropriate places
        for r in range(self.width):
            for c in range(self.height):
                # Set grid cell position properties
                rect = self.rect
                rect.pos = self.coordToPixelOffset(r, c)

                rect.draw()

# Consturct an empty grid of rowNum x colNum, with values placed at cells identified by rows and cols
def makeDisplayNumbers(rows, cols, values, rowNum, colNum):
    i = 0
    stimulus = []
    for r in range(rowNum):
        for c in range(colNum):
            if r in rows and c in cols:
                stimulus.append(values[i])
                i += 1
            else:
                stimulus.append(None)

    # reshape the list into an array of appropriate dimensions
    stimulus = np.array(stimulus)
    return np.reshape(stimulus, (rowNum, colNum))

# Adjust text output by -half a character in the x direction
halfCharPx = 10

win = visual.Window(
            size=[800, 800],
            units="pix",
            fullscr=False,
            color=[1, 1, 1]
        )

myMouse = event.Mouse(visible = False, win = win)


# Define experiment
exp = Experiment(trials=[
    TrialDigitSpan(
        stimulus=[
            makeDisplayNumbers(
                rows=[1],
                cols=[1],
                values=[randint(0, 9)],  # enforce no-repeat rule here late
                rowNum=4,
                colNum=4
            ) for y in range(4)
        ],
        stimulusDuration=.5,
        answers=[
            makeDisplayNumbers(
                rows=range(4),
                cols=[0],
                values=list(range(4)),
                rowNum=4, colNum=4
            ),
            makeDisplayNumbers(
                rows=range(4),
                cols=[0],
                values=[4,2,0,9],
                rowNum=4, colNum=4
            ),
            makeDisplayNumbers(
                rows=range(4),
                cols=[0],
                values=[7,9,2,8],
                rowNum=4, colNum=4
            )
        ],
        win=win
    ) for x in range(2)
])

exp.run()
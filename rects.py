import numpy as np
from psychopy import visual, clock, event
from math import floor, ceil
from random import randint, shuffle
from datetime import datetime


class Experiment:
    """
    The Experiment class simply holds values which must remain constant throughout the experiment.
    The values it holds are ones we define at creation time.
    Maybe later we'll add some default values to give an idea of how it should be used.
    """
    def __init__(self, **kwargs):
        """
        :param kwargs:
        """
        for k in kwargs.keys():
            self.__setattr__(k, kwargs[k])

    def run(self):
        for t in self.trials:
            t.run()



class Component:
    """
    Any set of screens in the experiment is a component. These could be trials, instructions, breaks, etc.
    """
    def __init__(self, experiment, **kwargs):
        """
        :type experiment: Experiment
        :param kwargs:
        """
        self.logEntries = []

        for k in kwargs.keys():
            self.__setattr__(k, kwargs[k])


    def log(self, entry, level = 'INFO'):
        """
        Write a log entry for this component
        :param entry: text to log
        :type entry: str
        :param level: notification level for entry
        :type level: str
        :return:
        """
        self.logEntries.append(str(datetime.now()) + ': ' + level + ' - ' + entry)


class Trial(Component):
    """
    Any values which might vary from trial to trial are recorded in a Trial
    """
    def __init__(self, win, **kwargs):
        """
        :param win: window in which to draw experiment
        :type win: Psychopy.visual.Window
        :param kwargs: keyword arguments
        """
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
        """
        :param kwargs:
        """
        super().__init__(**kwargs)

    def run(self):
        self.prepare()
        self.showStimulus()
        self.collectResponse()
        self.cleanup()

    def prepare(self):
        self.prepareAnswers()

        self.win.flip()
        self.log('Preparation complete for ' + str(self))
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
        self.log('Answer = ' + str(response["answer"]))
        self.log('Mouse position = ' + str(response["position"]))

        if response["answer"] == self.answerIndex:
            self.log('CORRECT!')
        else:
            self.log('WRONG!')

    def cleanup(self):
        print("\n".join(self.logEntries))

    def drawNumber(self, n):
        self.grid.draw()
        self.drawStim(n)
        self.win.flip()

    def prepareAnswers(self, override_existing=False):
        if hasattr(self, "answers") and not override_existing:
            return

        # Find the cell which has the value in it at each time point
        dim = np.shape(self.stimulus[0])
        nRows = dim[0]
        nCols = dim[1]
        values = self.stimulus[0]
        values = np.reshape(values, (1, np.prod(np.shape(values))))
        values = values[0]
        indices = np.where([values[i] is not None for i in range(np.prod(np.shape(values)))])
        indices = int(indices[0])  # only one answer!

        values = self.stimulus
        values = np.reshape(values, (len(values), np.prod(np.shape(values[0]))))

        answer = makeDisplayNumbers(
            rows=[1 for i in range(len(self.stimulus))],
            cols=[i for i in range(len(self.stimulus))],
            values=[stim[indices] for stim in values],
            rowNum=nRows,
            colNum=nCols
        )

        options = [answer]
        while len(options) < 3:
            values = list(range(10))
            shuffle(values)

            foil = makeDisplayNumbers(
                rows=[1 for i in range(len(self.stimulus))],
                cols=[i for i in range(len(self.stimulus))],
                values=[values[i] for i in range(4)],
                rowNum=nRows,
                colNum=nCols
            )

            if not any([np.array_equal(foil, o) for o in options]):
                options.append(foil)

        shuffle(options)
        self.answerIndex = np.where([np.array_equal(answer, o) for o in options])
        self.answerIndex = self.answerIndex[0][0]
        self.answers = options

        self.log('Target answer = ' + str(self.answerIndex))


    def getAnswerGridPositions(self, n, h, w):
        return [(
            win.size[0] / 2 - (self.grid.width + 1) * 25,
            win.size[1] / 2 - (self.grid.height + 1) * 25 - win.size[1] * i / n
        ) for i in range(n)]

    def getAnswerGrids(self):
        h = 25
        w = 25
        positions = self.getAnswerGridPositions(len(self.answers), h, w)
        return [
            Grid(
                width_in_cells=4,
                height_in_cells=4,
                # including the rectangles we'll be using as cells
                psychopy_rect=visual.Rect(
                    win=win,
                    width=w,
                    height=h,
                    fillColor=[1, 1, 1],
                    lineColor=[-1, -1, -1]
                ),
                start_pos_tuple=positions[i]
            ) for i in range(len(self.answers))
        ]

    def drawAnswerGrids(self):
        positions = self.getAnswerGridPositions(len(self.answers), 25, 25)
        grids = self.getAnswerGrids()
        for i in range(len(self.answers)):
            g = grids[i]
            g.draw()

            # Draw the puported answer over this grid
            self.drawStim(self.answers[i], grid=g)

    def getMouseInput(self):
        grids = self.getAnswerGrids()
        event.clearEvents()  # get rid of other, unprocessed events
        buttons, times = myMouse.getPressed(getTime=True)
        while True:
            buttons, times = myMouse.getPressed(getTime=True)

            if not buttons[0]:
                myMouse.clickReset()
                continue

            pos = myMouse.getPos()

            for a in range(len(grids)):
                g = grids[a]
                # check click is in the boundaries of the rectangle
                if g.clickIsIn(pos):
                    return {
                        "time": times,
                        "position": pos,
                        "answer": a
                    }



class TrialSpatialSpan(Trial):
    def __init__(self, **kwargs):
        super().__init__(kwargs)


    def prepareAnswers(self, override_existing=False):
        if hasAttr(self, answers) and not override_existing:
            return self.answers

        nRows = self.stimulus.size[0]
        nCols = self.stimulus.size[1]
        values = self.stimulus
        np.reshape(values, (1, np.prod(values.size)))
        values = values[0]
        indices = np.where(values is not None)

        answer = makeDisplayNumbers(
            rows=[floor(i / nCols) for i in indices],
            cols=[i % nCols for i in indices],
            values=values,
            nRows=nRows,
            nCols=nCols
        )
        foils = [makeDisplayNumbers() for i in range(2)]
        foils.append(answer)
        shuffle(foils)

        self.answers = foils



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

    def clickIsIn(self, coordinates):
        xmin = self.start[0]
        xmax = self.start[0] + self.width * self.rect.width
        ymin = self.start[1]
        ymax = self.start[1] + self.height * self.rect.height

        return xmin <= coordinates[0] <= xmax and ymin <= coordinates[1] <= ymax

def makeDisplayNumbers(rows, cols, values, rowNum, colNum):
    """
    Consturct an empty grid of rowNum x colNum, with values placed at cells identified by rows and cols
    :param rows: list of row indices
    :param cols: list of column indices
    :param values: list of values for cells identified by rows[i], cols[i]
    :param rowNum: number of rows in output
    :param colNum: number of columns in output
    :type rows: list
    :type cols: list
    :type values: list
    :type rowNum: int
    :type colNum: int
    :return: Numpy.nbarray with None in unspecified cells
    """
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

exp = Experiment()

# Define experiment
exp.trials = trials=[
    TrialDigitSpan(
        experiment=exp,
        stimulus=[
            makeDisplayNumbers(
                rows=[1],
                cols=[1],
                values=[randint(0, 9)],  # enforce no-repeat rule here later
                rowNum=4,
                colNum=4
            ) for y in range(4)
        ],
        stimulusDuration=.5,
        win=win
    ) for x in range(2)
]

exp.run()
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
    trials = []

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
    logEntries = []

    def __init__(self, experiment, **kwargs):
        """
        :type experiment: Experiment
        :param kwargs:
        """
        if experiment is None:
            raise ValueError('experiment must be specified')
        self.experiment = experiment

        for k in kwargs.keys():
            self.__setattr__(k, kwargs[k])

    def log(self, entry, level='INFO'):
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
    stimulus = None
    stimulusDuration = 0.5
    answerRectWidth = 25
    answerRectHeight = 25
    answers = []
    answer = -1             # Answer supplied by participant
    answerIndex = -1        # Actual answer

    def __init__(self, window, **kwargs):
        """
        :param win: window in which to draw experiment
        :type win: Psychopy.visual.Window
        :param kwargs: keyword arguments
        """
        super().__init__(**kwargs)
        self.win = window
        self.win.mouseVisible = True

        self.grid = Grid(
            width_in_cells=4,
            height_in_cells=4,
            # including the rectangles we'll be using as cells
            psychopy_rect=visual.Rect(
                win=self.win,
                width=50,
                height=50,
                fillColor=[1, 1, 1],
                lineColor=[-1, -1, -1]
            ),
            start_pos_tuple=(-(self.win.size[0] / 2), -(self.win.size[1] / 2))
        )

        for k in kwargs.keys():
            self.__setattr__(k, kwargs[k])

    def draw_stim(self, stimulus, grid=None):
        if grid is None:
            grid = self.grid

        dim = stimulus.shape
        for r in range(dim[0]):
            for c in range(dim[1]):
                if stimulus[r, c] is not None:
                    # nudge the x coordinate of the stimulus to centre it in the box
                    coords = grid.coord_to_pixel_offset(r, c)
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
# stimulus_duration {float} seconds to display each digit
class TrialDigitSpan(Trial):
    def __init__(self, **kwargs):
        """
        :param kwargs:
        """
        super().__init__(**kwargs)

    def run(self):
        self.prepare()
        self.show_stimulus()
        self.collect_response()
        self.cleanup()

    def prepare(self):
        self.prepare_answers()

        self.win.flip()
        self.log('Preparation complete for ' + str(self))
        clock.wait(.5)
        pass

    def show_stimulus(self):
        for n in self.stimulus:
            self.draw_number(n)
            clock.wait(self.stimulusDuration)

            self.grid.draw()
            self.win.flip()
            clock.wait(.5)

    def collect_response(self):
        # PsychoPy click response stuff?
        self.draw_answer_grids()
        self.win.flip()

        clock.wait(1)

        response = self.get_mouse_input()
        self.log('Answer = ' + str(response["answer"]))
        self.log('Mouse position = ' + str(response["position"]))

        if response["answer"] == self.answerIndex:
            self.log('CORRECT!')
        else:
            self.log('WRONG!')

    def cleanup(self):
        print("\n".join(self.logEntries))

    def draw_number(self, n):
        self.grid.draw()
        self.draw_stim(n)
        self.win.flip()

    def prepare_answers(self, override_existing=False):
        if hasattr(self, "answers") and not override_existing:
            return

        # Find the cell which has the value in it at each time point
        dim = np.shape(self.stimulus[0])
        n_rows = dim[0]
        n_cols = dim[1]
        values = self.stimulus[0]
        values = np.reshape(values, (1, np.prod(np.shape(values))))
        values = values[0]
        indices = np.where([values[i] is not None for i in range(int(np.prod(np.shape(values))))])
        indices = int(indices[0])  # only one answer!

        values = self.stimulus
        values = np.reshape(values, (len(values), np.prod(np.shape(values[0]))))

        answer = make_display_numbers(
            rows=[1] * len(self.stimulus),
            cols=[i for i in range(len(self.stimulus))],
            values=[stim[indices] for stim in values],
            row_num=n_rows,
            col_num=n_cols
        )

        options = [answer]
        while len(options) < 3:
            values = list(range(10))
            shuffle(values)

            foil = make_display_numbers(
                rows=[1] * len(self.stimulus),
                cols=[i for i in range(len(self.stimulus))],
                values=[values[i] for i in range(4)],
                row_num=n_rows,
                col_num=n_cols
            )

            if not any([np.array_equal(foil, o) for o in options]):
                options.append(foil)

        shuffle(options)
        self.answerIndex = np.where([np.array_equal(answer, o) for o in options])
        self.answerIndex = self.answerIndex[0][0]
        self.answers = options

        self.log('Target answer = ' + str(self.answerIndex))

    def get_answer_grid_positions(self):
        n = len(self.answers)
        return [(
            win.size[0] / 2 - (self.grid.width + 1) * self.answerRectWidth,
            win.size[1] / 2 - (self.grid.height + 1) * self.answerRectHeight - win.size[1] * i / n
        ) for i in range(n)]

    def get_answer_grids(self):
        positions = self.get_answer_grid_positions()
        return [
            Grid(
                width_in_cells=4,
                height_in_cells=4,
                # including the rectangles we'll be using as cells
                psychopy_rect=visual.Rect(
                    win=win,
                    width=self.answerRectWidth,
                    height=self.answerRectHeight,
                    fillColor=[1, 1, 1],
                    lineColor=[-1, -1, -1]
                ),
                start_pos_tuple=positions[i]
            ) for i in range(len(self.answers))
        ]

    def draw_answer_grids(self):
        grids = self.get_answer_grids()
        for i in range(len(self.answers)):
            g = grids[i]
            g.draw()

            # Draw the puported answer over this grid
            self.draw_stim(self.answers[i], grid=g)

    def get_mouse_input(self):
        grids = self.get_answer_grids()
        event.clearEvents()  # get rid of other, unprocessed events
        while True:
            buttons, times = myMouse.getPressed(getTime=True)

            if not buttons[0]:
                myMouse.clickReset()
                continue

            pos = myMouse.getPos()

            for a in range(len(grids)):
                g = grids[a]
                # check click is in the boundaries of the rectangle
                if g.click_is_in(pos):
                    return {
                        "time": times,
                        "position": pos,
                        "answer": a
                    }


class TrialSpatialSpan(Trial):
    def __init__(self, **kwargs):
        super().__init__(kwargs)

    def prepare_answers(self, override_existing=False):
        if hasattr(self, "answers") and not override_existing:
            return self.answers

        n_rows = self.stimulus.size[0]
        n_cols = self.stimulus.size[1]
        values = self.stimulus
        np.reshape(values, (1, np.prod(values.size)))
        values = values[0]
        indices = np.where(values is not None)

        answer = make_display_numbers(
            rows=[floor(i / n_cols) for i in indices],
            cols=[i % n_cols for i in indices],
            values=values,
            row_num=n_rows,
            col_num=n_cols
        )
        # foils = [make_display_numbers() for i in range(2)]
        # foils.append(answer)
        # shuffle(foils)
        #
        self.answers = answer


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
    def coord_to_pixel_offset(self, r, c):
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
                rect.pos = self.coord_to_pixel_offset(r, c)

                rect.draw()

    def click_is_in(self, coordinates):
        xmin = self.start[0]
        xmax = self.start[0] + self.width * self.rect.width
        ymin = self.start[1]
        ymax = self.start[1] + self.height * self.rect.height

        return xmin <= coordinates[0] <= xmax and ymin <= coordinates[1] <= ymax


def make_display_numbers(rows, cols, values, row_num, col_num):
    """
    Consturct an empty grid of rowNum x colNum, with values placed at cells identified by rows and cols
    :param rows: list of row indices
    :param cols: list of column indices
    :param values: list of values for cells identified by rows[i], cols[i]
    :param row_num: number of rows in output
    :param col_num: number of columns in output
    :type rows: list
    :type cols: list
    :type values: list
    :type row_num: int
    :type col_num: int
    :return: Numpy.nbarray with None in unspecified cells
    """
    i = 0
    stimulus = []
    for r in range(row_num):
        for c in range(col_num):
            if r in rows and c in cols:
                stimulus.append(values[i])
                i += 1
            else:
                stimulus.append(None)

    # reshape the list into an array of appropriate dimensions
    stimulus = np.array(stimulus)
    return np.reshape(stimulus, (row_num, col_num))


# Adjust text output by -half a character in the x direction
halfCharPx = 10

win = visual.Window(
    size=[800, 800],
    units="pix",
    fullscr=False,
    color=[1, 1, 1]
)

myMouse = event.Mouse(visible=False, win=win)

exp = Experiment()

# Define experiment
exp.trials = trials = [
    TrialDigitSpan(
        experiment=exp,
        stimulus=[
            make_display_numbers(
                rows=[1],
                cols=[1],
                values=[randint(0, 9)],  # enforce no-repeat rule here later
                row_num=4,
                col_num=4
            ) for y in range(4)
        ],
        stimulusDuration=.5,
        win=win
    ) for x in range(2)
]

exp.run()

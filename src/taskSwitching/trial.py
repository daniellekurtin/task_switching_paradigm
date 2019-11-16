from src.taskSwitching.component import *
from src.taskSwitching.grid import *


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
    stimulus = np.zeros((row_num, col_num))
    stimulus = np.where(stimulus == 0, None, stimulus)

    for i in range(len(values)):
        stimulus[rows[i], cols[i]] = values[i]

    return stimulus


class Trial(Component):
    """
    Any values which might vary from trial to trial are recorded in a Trial
    """
    trialNumber = -1
    stimulus = None
    stimulusDuration = 0.5
    answerRectWidth = 25
    answerRectHeight = 25
    answers = [None, None, None]
    answer = -1             # Answer supplied by participant
    answerIndex = -1        # Actual answer

    halfCharPx = 10

    def __init__(self, **kwargs):
        """
        :param win: window in which to draw experiment
        :type win: Psychopy.visual.Window
        :param kwargs: keyword arguments
        """
        self.logEntries = []
        super().__init__(**kwargs)

        self.grid = Grid(
            width_in_cells=4,
            height_in_cells=4,
            # including the rectangles we'll be using as cells
            psychopy_rect=visual.Rect(
                win=self.experiment.window,
                width=50,
                height=50,
                fillColor=[1, 1, 1],
                lineColor=[-1, -1, -1]
            ),
            start_pos_tuple=(-(self.experiment.window.size[0] / 2), -(self.experiment.window.size[1] / 2))
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
                    coords = (coords[0] - self.halfCharPx, coords[1])

                    stim = visual.TextStim(
                        text=stimulus[r, c],
                        win=self.experiment.window,
                        font='monospace',
                        pos=coords,
                        color=[-1, -1, 1],
                        wrapWidth=1  # no idea why we need this, but apparently we do. Complaints to PsychoPy :)
                    )
                    stim.draw()

    def get_answer_grid_positions(self):
        n = len(self.answers)
        return [(
            self.experiment.window.size[0] / 2 - (self.grid.width + 1) * self.answerRectWidth,
            self.experiment.window.size[1] / 2 - (self.grid.height + 1) *
            self.answerRectHeight - self.experiment.window.size[1] * i / n
        ) for i in range(n)]

    def get_answer_grids(self):
        positions = self.get_answer_grid_positions()
        return [
            Grid(
                width_in_cells=4,
                height_in_cells=4,
                # including the rectangles we'll be using as cells
                psychopy_rect=visual.Rect(
                    win=self.experiment.window,
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

            # Draw the purported answer over this grid
            self.draw_stim(self.answers[i], grid=g)

    def get_mouse_input(self):
        grids = self.get_answer_grids()
        my_mouse = event.Mouse(visible=True, win=self.experiment.window)
        event.clearEvents()  # get rid of other, unprocessed events
        while True:
            buttons, times = my_mouse.getPressed(getTime=True)

            if not buttons[0]:
                my_mouse.clickReset()
                continue

            pos = my_mouse.getPos()

            for a in range(len(grids)):
                g = grids[a]
                # check click is in the boundaries of the rectangle
                if g.click_is_in(pos):
                    return {
                        "time": times,
                        "position": pos,
                        "answer": a
                    }

    def draw_number(self, n):
        self.grid.draw()
        self.draw_stim(n)
        self.experiment.window.flip()

    def prepare(self):
        self.prepare_answers()

        self.experiment.window.flip()
        self.log('Preparation complete for trial number ' + str(self.trialNumber))
        clock.wait(.5)
        pass

    def show_stimulus(self):
        for n in self.stimulus:
            self.draw_number(n)
            clock.wait(self.stimulusDuration)

            self.grid.draw()
            self.experiment.window.flip()
            clock.wait(.5)

    def collect_response(self):
        # PsychoPy click response stuff?
        self.draw_answer_grids()
        self.experiment.window.flip()

        clock.wait(1)

        response = self.get_mouse_input()
        self.log('Answer = ' + str(response["answer"]))
        self.log('Mouse position = ' + str(response["position"]))

        if response["answer"] == self.answerIndex:
            self.log('CORRECT!')
        else:
            self.log('WRONG!')

    def prepare_answers(self):
        """
        This should be overridden by each child class
        :return:
        """
        pass

    def cleanup(self):
        print("\n".join(self.logEntries))

    def run(self):
        self.prepare()
        self.show_stimulus()
        self.collect_response()
        self.cleanup()

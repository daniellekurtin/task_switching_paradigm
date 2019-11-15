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


class Trial(Component):
    """
    Any values which might vary from trial to trial are recorded in a Trial
    """
    stimulus = None
    stimulusDuration = 0.5
    answerRectWidth = 25
    answerRectHeight = 25
    answers = [None, None, None]
    answer = -1             # Answer supplied by participant
    answerIndex = -1        # Actual answer

    halfCharPx = 10

    def __init__(self, window=None, **kwargs):
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
                    coords = (coords[0] - self.halfCharPx, coords[1])

                    stim = visual.TextStim(
                        text=stimulus[r, c],
                        win=self.win,
                        font='monospace',
                        pos=coords,
                        color=[-1, -1, 1],
                        wrapWidth=1  # no idea why we need this, but apparently we do. Complaints to PsychoPy :)
                    )
                    stim.draw()

    def run(self):
        # Run the whole trial, including collecting data
        pass




from taskSwitching.component import *
from taskSwitching.grid import *
from datetime import timedelta


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
    stimulus = np.zeros((row_num, col_num))
    stimulus = np.where(stimulus == 0, None, stimulus)

    for i in range(len(values)):
        stimulus[rows[i], cols[i]] = values[i]

    return stimulus


class Trial(Component):
    """
    Any values which might vary from trial to trial are recorded in a Trial
    """
    trial_number = -1
    stimulus = None
    answers = [None, None, None]
    answer = -1             # Answer supplied by participant
    answer_index = -1        # Actual answer

    halfCharPx = 10

    def __init__(self, experiment, **kwargs):
        """
        :param experiment: Experiment to which this trial belongs
        :type experiment: taskSwitching.Experiment
        :param kwargs: keyword arguments
        """
        self.logEntries = []
        super().__init__(experiment, **kwargs)

        cell_size = 70  # pixels
        grid_size = 4   # cells

        self.grid = Grid(
            width_in_cells=grid_size,
            height_in_cells=grid_size,
            # including the rectangles we'll be using as cells
            psychopy_rect=visual.Rect(
                win=self.experiment.window,
                width=cell_size,
                height=cell_size,
                fillColor=[0, 0, 0],
                lineColor=[1, 1, 1]
            ),
            start_pos_tuple=(
                -(self.experiment.window.size[0] / 2) + cell_size * grid_size,
                0
            )
        )

        # Inherit trial-specific properties of the Experiment
        if hasattr(experiment, 'stimulus_duration'):
            self.stimulus_duration = experiment.stimulus_duration
        if hasattr(experiment, 'answer_rect_width'):
            self.answer_rect_width = experiment.answer_rect_width
        if hasattr(experiment, 'answer_rect_height'):
            self.answer_rect_height = experiment.answer_rect_height
        if hasattr(experiment, 'delay_before_response'):
            self.delay_before_response = experiment.delay_before_response
        if hasattr(experiment, 'max_response_time'):
            self.max_response_time = experiment.max_response_time

        for k in kwargs.keys():
            self.__setattr__(k, kwargs[k])

    def draw_stim(self, stimulus, grid=None):
        if grid is None:
            grid = self.grid

        dim = stimulus.shape
        for r in range(dim[0]):
            for c in range(dim[1]):
                if stimulus[r, c] is not None:
                    coords = grid.coord_to_pixel_offset(r, c)
                    # Shaded box
                    grid.rect.pos = coords
                    color = grid.rect.fillColor
                    grid.rect.fillColor = [.5, .5, .5]
                    grid.rect.draw()
                    grid.rect.fillColor = color

                    # Draw the text
                    # Nudge the x coordinate of the stimulus to centre it in the box
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
            self.experiment.window.size[0] / 2 - (self.grid.width + 1) * self.answer_rect_width,
            self.experiment.window.size[1] / 2 - self.grid.height *
            self.answer_rect_height - self.experiment.window.size[1] * i / n
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
                    width=self.answer_rect_width,
                    height=self.answer_rect_height,
                    fillColor=[0, 0, 0],
                    lineColor=[1, 1, 1]
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

    def draw_number(self, n):
        self.grid.draw()
        self.draw_stim(n)
        self.experiment.window.flip()

    def prepare(self):
        super().prepare()
        self.prepare_answers()

        self.experiment.window.flip()
        self.log('Preparation complete for trial number ' +
                 str(self.trial_number) +
                 ' (' + self.__class__.__name__ + ')')
        clock.wait(.5)
        pass

    def show_stimulus(self):
        for n in self.stimulus:
            self.draw_number(n)
            clock.wait(self.stimulus_duration)

            self.grid.draw()
            self.experiment.window.flip()
            clock.wait(.5)

    def collect_response(self):
        # PsychoPy click response stuff?
        self.draw_answer_grids()
        self.experiment.window.flip()

        clock.wait(self.delay_before_response)

        t0 = self.experiment.synch.clock
        self.experiment.synch.wait_for_button(timeout=self.max_response_time)
        if len(self.experiment.synch.buttonpresses):
            button = self.experiment.synch.buttonpresses[-1][0]

            self.log('Answer = ' + str(button),level='EXP')
            self.log('Reaction time = ' + str(self.experiment.synch.buttonpresses[-1][1]-t0),level='EXP')
            self.log('Correct = ' + str(button == self.answer_index),level='EXP') #  button is not zero-indexed
        else:
            self.log('Answer = ' + str(None),level='EXP')
            self.log('Reaction time = ' + str(0),level='EXP')
            self.log('Correct = ' + str(False),level='EXP')

    def prepare_answers(self):
        """
        This should be overridden by each child class
        :return:
        """
        pass

    def main(self):
        self.trial_number = self.experiment.current_trial_number
        self.experiment.current_trial_number += 1

        self.show_stimulus()
        self.collect_response()

    def to_csv(self):
        pass

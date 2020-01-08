from taskSwitching.component import *
from taskSwitching.grid import *
from datetime import timedelta


def make_display_numbers(rows, cols, values, row_num, col_num):
    """
    Construct an empty grid of rowNum x colNum, with values placed at cells identified by rows and cols
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
    version = "v0.0.1"  # used for keeping .csv file headers sensible

    trial_number = -1
    stimulus = None
    answers = [None, None, None]
    answer = -1  # Answer supplied by participant
    answer_index = -1  # Actual answer

    times = {
        "start": -1,
        "stimulus_start": -1,
        "stimulus_end": -1,
        "response_enabled": -1,
        "response_submitted": -1,
        "response_disabled": -1,
        "trial_logged": -1
    }

    def __init__(self, experiment, **kwargs):
        """
        :param experiment: Experiment to which this trial belongs
        :type experiment: taskSwitching.Experiment
        :param kwargs: keyword arguments
        """
        self.logEntries = []
        super().__init__(experiment, **kwargs)

        cell_size = .14  # normed units of Panel
        cell_pix = self.n2p([cell_size, 0])[0]
        grid_size = 6  # cells

        self.grid = Grid(
            width_in_cells=grid_size,
            height_in_cells=grid_size,
            # including the rectangles we'll be using as cells
            psychopy_rect=visual.Rect(
                win=self.experiment.window,
                width=cell_pix,
                height=cell_pix,
                units='pix',
                fillColor=[0, 0, 0],
                lineColor=[1, 1, 1]
            ),
            start_coords=self.n2p([-.9 + (cell_size * grid_size / 2), 0])
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

    def draw_stim(self, stimulus, target_grid=None):
        if target_grid is None:
            target_grid = self.grid

        dim = stimulus.shape
        for r in range(dim[0]):
            for c in range(dim[1]):
                if stimulus[r, c] is not None:
                    coords = target_grid.coord_to_pixel_offset(r, c)
                    # Shaded box
                    target_grid.rect.pos = coords
                    color = target_grid.rect.fillColor
                    target_grid.rect.fillColor = self.experiment.stimulus_background_color
                    target_grid.rect.draw()
                    target_grid.rect.fillColor = color

                    # Draw the text
                    stim = visual.TextStim(
                        text=stimulus[r, c],
                        win=self.experiment.window,
                        font='monospace',
                        pos=coords,
                        color=self.experiment.stimulus_text_color
                    )
                    stim.draw()

    def get_answer_grid_positions(self):
        n = len(self.answers)
        remainder = 2 - (self.answer_rect_height * n)
        gap_height = remainder / (n + 1)
        return [[
            .60 + self.answer_rect_width / 2,  # x
            (1 - (gap_height + self.answer_rect_height / 2)) - (gap_height + self.answer_rect_height) * i  # y
        ] for i in range(n)]

    def get_answer_grids(self):
        positions = self.get_answer_grid_positions()
        [width, height] = self.n2p([self.answer_rect_width, self.answer_rect_height])
        return [
            Grid(
                width_in_cells=self.experiment.grid_size,
                height_in_cells=self.experiment.grid_size,
                # including the rectangles we'll be using as cells
                psychopy_rect=visual.Rect(
                    win=self.experiment.window,
                    width=width,
                    height=height,
                    units='pix',
                    fillColor=self.experiment.background_color,
                    lineColor=self.experiment.line_color
                ),
                start_coords=self.n2p(positions[i])
            ) for i in range(len(self.answers))
        ]

    def draw_answer_grids(self):
        grids = self.get_answer_grids()
        for i in range(len(self.answers)):
            g = grids[i]
            g.draw()

            # Draw the purported answer over this grid
            self.draw_stim(self.answers[i], target_grid=g)

    def draw_number(self, n):
        self.debug_visuals()
        self.grid.draw()
        self.draw_stim(n)
        self.experiment.window.flip()

    def draw_response_feedback(self):
        grids = self.get_answer_grids()
        g = grids[self.answer]
        g.draw()
        self.draw_stim(self.answers[self.answer], target_grid=g)
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
        self.times["stimulus_start"] = self.experiment.synch.clock

        for n in self.stimulus:
            self.draw_number(n)
            clock.wait(self.stimulus_duration)

            self.debug_visuals()
            self.grid.draw()
            self.experiment.window.flip()
            clock.wait(.5)

        self.times["stimulus_end"] = self.experiment.synch.clock

    def collect_response(self):
        # PsychoPy click response stuff?
        self.debug_visuals()
        self.draw_answer_grids()
        self.experiment.window.flip()

        clock.wait(self.delay_before_response)

        self.times["response_enabled"] = self.experiment.synch.clock

        self.experiment.synch.wait_for_button(timeout=self.max_response_time)
        if len(self.experiment.synch.buttonpresses):
            self.answer = self.experiment.synch.buttonpresses[-1][0]  # button is not zero-indexed
            self.times["response_submitted"] = self.experiment.synch.buttonpresses[-1][1]

            padding_time = self.experiment.synch.clock + self.max_response_time - self.times["response_enabled"]

            self.draw_response_feedback()

            if padding_time > 0:
                clock.wait(padding_time)
        else:
            self.answer = -1
            self.times["response_submitted"] = -1

        self.times["response_disabled"] = self.experiment.synch.clock

        self.log('Answer = ' + str(self.answer), level='EXP')
        self.log('Response time = ' + str(self.times["response_submitted"] - self.times["response_enabled"]),
                 level='EXP')
        self.log('Correct = ' + str(self.answer == self.answer_index), level='EXP')

    def prepare_answers(self):
        """
        This should be overridden by each child class
        :return:
        """
        pass

    def main(self):
        self.times["start"] = self.experiment.synch.clock

        self.trial_number = self.experiment.current_trial_number
        self.experiment.current_trial_number += 1

        self.show_stimulus()
        self.collect_response()

        self.to_csv()

    def to_csv(self):
        self.times["trial_logged"] = self.experiment.synch.clock

        self.experiment.save_csv(
            {
                "trial_py_version": self.version,
                "type": self.__class__.__name__,
                "target_ans": self.answer_index,
                "participant_ans": self.answer,
                "time_start": self.times["start"],
                "time_stimulus_start": self.times["stimulus_start"],
                "time_stimulus_end": self.times["stimulus_end"],
                "time_response_enabled": self.times["response_enabled"],
                "time_response_submitted": self.times["response_submitted"],
                "time_response_disabled": self.times["response_disabled"],
                "time_trial_logged": self.times["trial_logged"]
            },
            file="trials-" + self.version,
            public=True
        )

from taskSwitching.component import *
from taskSwitching.grid import *


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
    version = "v0.0.2"  # used for keeping .csv file headers sensible

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
        "feedback_start": -1,
        "feedback_end": -1,
        "trial_logged": -1
    }

    def __init__(self, experiment, trial_type="undefined", **kwargs):
        """
        :param experiment: Experiment to which this trial belongs
        :param trial_type: This tells trials what task type they are 
        :type experiment: taskSwitching.Experiment
        :param kwargs: keyword arguments
        """
        self.logEntries = []
        super().__init__(experiment, **kwargs)
        self.trial_type = trial_type

        cell_size = .14  # normed units of Panel
        cell_pix = self.n2p([cell_size, 0])[0]
        grid_size = 6  # cells

        if self.experiment.window:
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
                start_coords=self.n2p([(-.4 + cell_size * grid_size / 2), 0])
            )

        # Inherit trial-specific properties of the Experiment
        ########################################################################################

        # Find out my stimulus_durations:
        # Plan A, I'll check my experiment to see if there is a dictionary of values for stimulus_durations,  
        # and whether there is a stimulus_duration for my trial_type. 
        # Plan B, I'll check my experiment to see if it has stimulus_duration, and use the value it has for stimulus_duration  
        # Plan C, check to see if I have a constant simulus_duration I can use for my trials (kwargs)

        if hasattr(experiment, 'stimulus_durations') and trial_type in experiment.stimulus_durations:   # Plan A
            self.stimulus_duration = experiment.stimulus_durations[trial_type]  
        elif hasattr(experiment, 'stimulus_duration'):     # Plan B
            self.stimulus_duration = experiment.stimulus_duration

        if hasattr(experiment, 'feedback_durations') and trial_type in experiment.feedback_durations:  # Plan A
            self.feedback_duration = experiment.feedback_durations[trial_type]
        elif hasattr(experiment, 'feedback_duration'):  # Plan B
            self.feedback_duration = experiment.feedback_duration
        # Plan C is taken care of at the bottom with kwargs

        if hasattr(experiment, 'answer_rect_width'):
            self.answer_rect_width = experiment.answer_rect_width
        if hasattr(experiment, 'answer_rect_height'):
            self.answer_rect_height = experiment.answer_rect_height
        if hasattr(experiment, 'delay_before_response'):
            self.delay_before_response = experiment.delay_before_response
        if hasattr(experiment, 'max_response_time'):
            self.max_response_time = experiment.max_response_time
        if hasattr(experiment, 'feedback_color'):
            self.feedback_color = experiment.feedback_color
        if hasattr(experiment, 'save_enabled'):
            self.save_enabled = experiment.save_enabled

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
        remainder = 3 - (self.answer_rect_height * n)
        gap_height = remainder / (n + 1)
        
        return [[
            (-1.4 + (gap_height - self.answer_rect_width / 2)) + (gap_height - self.answer_rect_height) * i,  # x
            -.03 + self.answer_rect_width / 2  # y

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
        # clock.wait(.5)
        pass

    def show_stimulus(self):
        self.times["stimulus_start"] = self.experiment.synch.clock

        for n in self.stimulus:
            self.draw_number(n)
            clock.wait(self.stimulus_duration)
            # if self.task_type_ds:
            #     clock.wait(self.stimulus_duration_ds)
            # elif experiment_task_switch.TrialTypes == experiment_task_switch.TrialTypes.SPATIAL_SPAN:
            #     clock.wait(self.stimulus_duration_ss)
            # elif experiment_task_switch.TrialTypes == experiment_task_switch.TrialTypes.SPATIAL_ROTATION:
            #     clock.wait(self.stimulus_duration_sr)
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

    def show_feedback(self):
        """
        Provide a visual indicator of the correct answer
        :return:
        """
        self.times["feedback_start"] = self.experiment.synch.clock
        if self.feedback_duration > 0:
            # Draw a big green rectangle to show the position of the correct answer grid
            target = self.get_answer_grids()[self.answer_index]
            target.rect.lineColor = [-1, 1, -1]
            target.draw()

            size = (target.rect.width * target.width, target.rect.height * target.height)
            gap_size = 6
            border_size = 12
            feedback_big = Grid(
                width_in_cells=1,
                height_in_cells=1,
                psychopy_rect=visual.Rect(
                    win=self.experiment.window,
                    width=size[0] + gap_size + border_size * 2,
                    height=size[1] + gap_size + border_size * 2,
                    units='pix',
                    fillColor=self.feedback_color,
                    lineColor=self.experiment.background_color
                ),
                start_coords=[
                    target.start[0] + size[0] + target.rect.width / 2 - border_size / 2 - gap_size / 2,
                    target.start[1] + size[1] + target.rect.height / 2 - border_size / 2 - gap_size / 2
                ]
            )
            feedback_small = Grid(
                width_in_cells=1,
                height_in_cells=1,
                psychopy_rect=visual.Rect(
                    win=self.experiment.window,
                    width=size[0] + gap_size,
                    height=size[1] + gap_size,
                    units='pix',
                    fillColor=self.experiment.background_color,
                    lineColor=self.experiment.background_color
                ),
                start_coords=[
                    target.start[0] + size[0] + target.rect.width / 2 - border_size - gap_size * 1.5,
                    target.start[1] + size[1] + target.rect.height / 2 - border_size - gap_size * 1.5
                ]
            )
            feedback_big.draw()
            feedback_small.draw()
            self.draw_response_feedback()
            clock.wait(self.feedback_duration)

        self.experiment.window.flip()
        self.times["feedback_end"] = self.experiment.synch.clock

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
        self.show_feedback()

        self.to_csv()

    def to_csv(self):
        if not self.save_enabled:
            return

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
                "time_trial_logged": self.times["trial_logged"],
            },
            file="trials-" + self.version,
            public=True
        )

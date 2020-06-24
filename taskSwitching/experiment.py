#!F:\xampp\htdocs\oxbridge_brainhack_2019\venv\Scripts\Python.exe
from psychopy import visual
import csv
from os import getcwd, path, makedirs
from datetime import datetime
import enum


class Experiment:
    """
    The Experiment class simply holds values which must remain constant throughout the experiment.
    The values it holds are ones we define at creation time.
    Maybe later we'll add some default values to give an idea of how it should be used.
    """
    version = "v0.0.7"
    
    trials = []
    current_trial_number = 0
    stimulus_duration = 0.5   # if you want multiple values, use stimulus_durations instead
    feedback_duration = 2  # if you want multiple values, use feedback_durations instead

    panel_size = [800, 800]

    grid_size = 6

    delay_before_response = 0.15
    max_response_time = 3
    answer_rect_width = .06   # normed units for Panel
    answer_rect_height = .06  # normed units for Panel

    background_color = [0, 0, 0]
    feedback_color = [-1, 1, -1]
    line_color = [1, 1, 1]
    text_color = [1, 1, 1]
    stimulus_text_color = [-1, -1, 1]
    stimulus_background_color = [.5, .5, .5]

    def __init__(self, participant=None, window=None, synch=None, config=None, online=False, **kwargs):
        """
        :param kwargs:
        """
        if not online:
            if participant is None:
                raise ValueError('A participant must be specified for the experiment')

            if window is None:
                raise ValueError('A window must be specified for the experiment')

            if synch is None:
                raise ValueError('A synch object must be specified for the experiment')

            if config is None:
                raise ValueError('A configuration must be specified for the experiment')

        self.participant = participant
        self.window = window
        self.synch = synch
        self.Config = config
        if config is not None:
            self.log_level = self.Config.MIN_LOG_LEVEL.value

        if self.window:
            self.loading_text_stim = visual.TextStim(
                win=self.window,
                color=self.text_color,
                text=""
            )

        for k in kwargs.keys():
            self.__setattr__(k, kwargs[k])

        self.save_path = path.join(getcwd(), "data")
        if not online:
            makedirs(path.join(self.save_path,"private"), exist_ok=True)
            makedirs(path.join(self.save_path,"public"), exist_ok=True)

        if self.window:
            if self.window.size[0] < self.panel_size[0] or self.window.size[1] < self.panel_size[1]:
                raise ValueError('The requested panel size is larger than the window size')

            self.window.color = self.background_color

    def __del__(self):
        if self.window:
            self.window.close()
        self.synch = None

    def run(self):
        for t in self.trials:
            t.run()
            if hasattr(self.synch, 'pressed_control_buttons') and \
                    self.Config.QUIT_BUTTON.value in self.synch.pressed_control_buttons():
                print('{}: {} - {}'.format(str(datetime.now()), 'INFO', 'Experiment has been interrupted'))
                break

    def save_csv(self, row_dict, file="trials", public=True):
        """
        Write a line to the experiment's CSV file
        :param row_dict: dict of values to write
        :type row_dict: dict
        :param file: filename to save under
        :type file: str
        :param public: whether data should be publicly accesible
        :type public: bool
        :return:
        """
        if public:
            access = "public"
        else:
            access = "private"
        file_name = path.join(self.save_path, access, self.__class__.__name__ + "-" + self.version + "_" + file + ".csv")

        # add write-time info to the file
        row_dict = {
            'write_time': datetime.now().isoformat(),
            'experiment_name': self.__class__.__name__,
            'experiment_version': self.version,
            'participant_id': self.participant.id,
            'participant_session': self.participant.session,
            'participant_age': self.participant.age,
            'participant_gender': self.participant.gender,
            'cue_length': self.break_duration,
            **row_dict
        }

        if not path.isfile(file_name):
            head = row_dict.keys()
            new_file = True
        else:
            new_file = False
            with open(file_name, 'r') as f:
                old = csv.DictReader(f)
                head = old.fieldnames

                for k in row_dict.keys():
                    if k not in head:
                        raise ValueError("Field " + k + " in data but not header names when saving to " + file_name)

                for k in head:
                    if k not in row_dict.keys():
                        raise ValueError("Field " + k + " in headers but not in data when saving to " + file_name)


        if len(head) < 5:
            raise ValueError("No headers found for saving CSV file " + file_name)
        
        

        with open(file_name, 'a+', newline='') as f:
            w = csv.DictWriter(f, head)
            if new_file:
                w.writeheader()

            w.writerow(row_dict)

    def to_json(self):
        """
        Save a JSON representation of the experimental parameters
        :return:
        """
        pass

    def trial_order_to_string(self):
        n = 0
        lines = []
        for i in range(len(self.trials)):
            t = self.trials[i]
            tt = t.__class__.__name__
            # output the final trial type
            lines.append(str(n) + " x " + str(tt))

            n += 1

        return lines


    def debug_trial_order(self):
        for s in self.trial_order_to_string():
            print("> " + s)


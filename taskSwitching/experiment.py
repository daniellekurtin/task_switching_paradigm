from psychopy import visual
import csv
import os.path
import datetime


class Experiment:
    """
    The Experiment class simply holds values which must remain constant throughout the experiment.
    The values it holds are ones we define at creation time.
    Maybe later we'll add some default values to give an idea of how it should be used.
    """
    version = "v0.0.1"
    save_path = "data"

    trials = []
    current_trial_number = 0
    stimulus_duration = 0.5

    panel_size = [800, 800]

    grid_size = 6

    delay_before_response = 0.15
    max_response_time = 3
    answer_rect_width = .06   # normed units for Panel
    answer_rect_height = .06  # normed units for Panel

    background_color = [0, 0, 0]
    line_color = [1, 1, 1]
    text_color = [1, 1, 1]
    stimulus_text_color = [-1, -1, 1]
    stimulus_background_color = [.5, .5, .5]

    def __init__(self, participant=None, window=None, synch=None, log_level='INFO', **kwargs):
        """
        :param kwargs:
        """
        if participant is None:
            raise ValueError('A participant must be specified for the experiment')
        else:
            self.participant = participant

        if window is None:
            raise ValueError('A window must be specified for the experiment')
        else:
            self.window = window

        if synch is None:
            raise ValueError('A synch object must be specified for the experiment')
        else:
            self.synch = synch
        
        self.log_level = log_level

        for k in kwargs.keys():
            self.__setattr__(k, kwargs[k])

        if self.window.size[0] < self.panel_size[0] or self.window.size[1] < self.panel_size[1]:
            raise ValueError('The requested panel size is larger than the window size')

        self.window.color = self.background_color

        self.loading_text_stim = visual.TextStim(
            win=self.window,
            color=self.text_color,
            text=""
        )

    def __del__(self):
        self.window.close()
        self.synch = None

    def run(self):
        for t in self.trials:
            t.run()

    def save_csv(self, row_dict, file="trials", public=False):
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
        file_name = os.path.join(self.save_path, access, self.__class__.__name__ + "_" + file + ".csv")

        # add write-time info to the file
        row_dict = {
            'write_time': datetime.datetime.now().isoformat(),
            'experiment_name': self.__class__.__name__,
            'experiment_version': self.version,
            'participant_id': self.participant["id"],
            **row_dict
        }

        if not os.path.isfile(file_name):
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

        with open(file_name, 'a+') as f:
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

    def debug_trial_order(self):
        n = 0
        for i in range(len(self.trials)):
            t = self.trials[i]
            tt = t.__class__.__name__
            # print the final trial type
            print("> " + str(n) + " x " + str(tt))

            n += 1



class Experiment:
    """
    The Experiment class simply holds values which must remain constant throughout the experiment.
    The values it holds are ones we define at creation time.
    Maybe later we'll add some default values to give an idea of how it should be used.
    """
    trials = []
    current_trial_number = 0
    stimulus_duration = 0.5

    panel_size = [800, 800]

    grid_size = 6

    delay_before_response = 0.5
    max_response_time = 2
    answer_rect_width = .06   # normed units for Panel
    answer_rect_height = .06  # normed units for Panel

    def __init__(self, window=None, synch=None, log_level='INFO', **kwargs):
        """
        :param kwargs:
        """
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

    def __del__(self):
        self.window.close()
        self.synch = None

    def run(self):
        for t in self.trials:
            t.run()

    def save_csv(self, line):
        """
        Write a line to the experiment's CSV file
        :param line: list of values to write
        :type line: list
        :return:
        """
        pass

    def to_json(self):
        """
        Save a JSON representation of the experimental parameters
        :return:
        """
        pass

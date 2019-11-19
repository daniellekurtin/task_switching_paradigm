class Experiment:
    """
    The Experiment class simply holds values which must remain constant throughout the experiment.
    The values it holds are ones we define at creation time.
    Maybe later we'll add some default values to give an idea of how it should be used.
    """
    trials = []
    stimulus_duration = 0.5
    answer_rect_width = 40
    answer_rect_height = 40

    def __init__(self, window=None, **kwargs):
        """
        :param kwargs:
        """
        if window is None:
            raise ValueError('A window must be specified for the experiment')
        else:
            self.window = window

        for k in kwargs.keys():
            self.__setattr__(k, kwargs[k])

    def run(self):
        for t in self.trials:
            t.run()


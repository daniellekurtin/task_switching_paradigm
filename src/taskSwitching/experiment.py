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


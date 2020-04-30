from taskSwitching.component import *


class ComponentRest(Component):
    """
    Break from performing the tasks, first attribute is its duration in seconds

    Examples
    -------
    >>> exp = tS.Experiment()
    >>> win = visual.Window(
    >>>             size=[800, 800],
    >>>             units="pix",
    >>>             fullscr=False,
    >>>             color=[1, 1, 1]
    >>>             )
    >>> rest = [tS.ComponentRest(120, window=win, experiment=exp)]
    >>> exp.trials = rest
    >>> exp.run()
    """

    def __init__(self, break_duration=120, **kwargs):

        super().__init__(**kwargs)
        if self.experiment.window:
            self.experiment.window.mouseVisible = True
            self.countdown = visual.TextStim(
                self.experiment.window,
                text="",
                color=self.experiment.text_color
            )

        self.duration = break_duration

        for k in kwargs.keys():
            self.__setattr__(k, kwargs[k])

    def draw(self):
        self.countdown.draw()

    def main(self):
        # Will show a fixation cross and a countdown in seconds
        # For a countdown of 5 seconds, final_countdown needs 
        # self.duration - 6
        end_time = 0
        final_countdown = 114
        while end_time < self.duration:
            if end_time < final_countdown:
                self.countdown.text = str("+")
            if final_countdown < end_time:
                self.countdown.text = str(self.duration - end_time)

            self.draw()
            clock.wait(1)
            self.experiment.window.flip()
            end_time += 1


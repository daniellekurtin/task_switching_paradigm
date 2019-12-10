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
        self.experiment.window.mouseVisible = True
        self.duration = break_duration
        self.fixation = visual.ShapeStim(
            self.experiment.window,
            vertices=((0, -0.5), (0, 0.5), (0, 0), (-0.5, 0), (0.5, 0)),
            lineWidth=5,
            closeShape=False,
            lineColor=[-1, -1, -1]
        )
        self.countdown = visual.TextStim(
            self.experiment.window,
            text="",
            color=[-1, -1, -1],
            pos=(
                self.experiment.window.size[0] / 2 - 20,
                150
            )
        )

        for k in kwargs.keys():
            self.__setattr__(k, kwargs[k])

    def draw(self):
        self.fixation.draw()
        self.countdown.draw()

    def main(self):
        # Will show a fixation cross and a countdown in seconds
        end_time = 0
        while end_time < self.duration:
            self.countdown.text = str(self.duration - end_time)
            self.draw()
            clock.wait(1)
            self.experiment.window.flip()
            end_time += 1


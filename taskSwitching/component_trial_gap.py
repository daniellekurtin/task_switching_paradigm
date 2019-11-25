from taskSwitching.component_rest import *


class ComponentTrialGap(ComponentRest):
    """
    Gap between trials. Simply waits.
    """

    def __init__(self, break_duration=1.0, **kwargs):

        super().__init__(**kwargs)

        self.break_duration = break_duration

        for k in kwargs.keys():
            self.__setattr__(k, kwargs[k])

    def main(self):
        # Will show a fixation cross and a countdown in seconds
        self.draw()
        self.experiment.window.flip()
        clock.wait(self.break_duration)

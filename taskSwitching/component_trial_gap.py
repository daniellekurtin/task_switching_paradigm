from taskSwitching.component_rest import *
import random   


class ComponentTrialGap(ComponentRest):
    """
    Gap between trials. Simply waits.
    """

    def __init__(self, break_duration=.1, plus_jitter_max=1, **kwargs):  

        super().__init__(**kwargs)

        jitter_duration = random.random() * plus_jitter_max 
        self.break_duration = break_duration + jitter_duration 

        for k in kwargs.keys():
            self.__setattr__(k, kwargs[k])

    def main(self):
        # Will show a fixation cross and a countdown in seconds
        self.draw()
        self.experiment.window.flip()
        clock.wait(self.break_duration)

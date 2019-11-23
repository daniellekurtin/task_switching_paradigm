from taskSwitching.component_rest import *


class ComponentInfoCard(ComponentRest):
    """
    Shows the next task type information.
    """

    def __init__(self, next_task, break_duration=.5, **kwargs):

        super().__init__(**kwargs)

        self.next_task = next_task
        self.break_duration = break_duration

        for k in kwargs.keys():
            self.__setattr__(k, kwargs[k])

    def main(self):
        # Will show a fixation cross and a countdown in seconds
        self.countdown.text = "Next Task: " + self.next_task
        self.draw()
        self.experiment.window.flip()
        clock.wait(self.break_duration)

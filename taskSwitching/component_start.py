from taskSwitching.component_rest import *


class ComponentStart(ComponentRest):
    """
    Shows the next task type information.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        for k in kwargs.keys():
            self.__setattr__(k, kwargs[k])


    def main(self):
        # Will show the start card and wait for a keypress
        self.countdown.text = "Press any key to begin" 
        self.draw()
        self.experiment.window.flip()
        
        self.experiment.synch.wait_for_button()

        

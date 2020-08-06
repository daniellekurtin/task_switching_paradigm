import unittest
from psychopy import visual
import taskSwitching


class TestFunctionality(unittest.TestCase):

    def test_experiment_setup(self):
        with self.assertRaisesRegex(ValueError, r"A participant must be specified for the experiment"):
            taskSwitching.Experiment()

        participant = taskSwitching.Participant()
        with self.assertRaisesRegex(ValueError, r"A window must be specified for the experiment"):
            taskSwitching.Experiment(participant=participant)

        # window = visual.Window(
        #     size=[1000, 1000],
        #     units="pix",
        #     fullscr=False,
        #     color=[0, 0, 0],
        #     winType='pyglet',
        #     gammaErrorPolicy="warn"
        # )
        # with self.assertRaisesRegex(ValueError, r"A synch object must be specified for the experiment"):
        #     taskSwitching.Experiment(participant=participant, window=window)

        # We can add more tests for that here

    # We can define and add more tests here


if __name__ == '__main__':
    unittest.main()

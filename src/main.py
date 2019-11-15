"""
Jobs:
    * Move to a window-relative rather than absolute sizing approach (all)
    * Saving results to CSV (Trial)
    * Saving Components to JSON (Component)
    * Non-trial Components content
        * Breaks (ComponentRest)
        * Instructions (ComponentText)
    * Tidy TrialDigitSpan (TrialDigitSpan)
        * Answer grids in correct order
    * Content for other trial types (TrialSpatialSpan, TrialSpatialRotation)
    * Component sequence production (__main__)
    * Single definitions only (DRY)
        * window should be defined in Experiment and referred to via experiment in its children
"""
import src.taskSwitching as tS
from psychopy import visual
from random import randint

win = visual.Window(
    size=[800, 800],
    units="pix",
    fullscr=False,
    color=[1, 1, 1]
)

exp = tS.Experiment()

# Define experiment
exp.trials = trials = [
    tS.TrialDigitSpan(
        experiment=exp,
        stimulus=[
            tS.make_display_numbers(
                rows=[1],
                cols=[1],
                values=[randint(0, 9)],  # enforce no-repeat rule here later
                row_num=4,
                col_num=4
            ) for y in range(4)
        ],
        stimulusDuration=.5,
        window=win
    ) for x in range(2)
]

exp.run()

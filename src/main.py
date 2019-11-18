"""
Jobs:
    * Move to a window-relative rather than absolute units approach (all)
        * We should be positioning the grids using window-relative (normalised) units
        * Stimuli should still be specified in pixels
        * Alternatively we could use a degrees of visual angle approach
        * This should improve flexibility and durability of the project
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
    * Package unit tests (all)
    * Reordering the files to put them into a more intuitive order
"""
import src.taskSwitching as tS
from psychopy import visual
from random import shuffle

win = visual.Window(
    size=[800, 800],
    units="pix",
    fullscr=False,
    color=[0, 0, 0]
)

exp = tS.Experiment(window=win)

n = 5

stimuli = {
    "SpatialSpan": tS.get_spatial_span_stimuli(n),
    "DigitSpan": tS.get_digit_span_stimuli(n)
}

# Define experiment
ss = [
    tS.TrialSpatialSpan(
        trialNumer=i,
        experiment=exp,
        stimulus=stimuli["SpatialSpan"][i],
        stimulusDuration=.5
    ) for i in range(len(stimuli["SpatialSpan"]))
]

ds = [
    tS.TrialDigitSpan(
        trialNumber=i,
        experiment=exp,
        stimulus=stimuli["DigitSpan"][i],
        stimulusDuration=.5
    ) for i in range(len(stimuli["DigitSpan"]))
]

trials = ss + ds
shuffle(trials)
trials.insert(n, tS.ComponentRest(break_duration=5, experiment=exp))

exp.trials = trials

exp.run()

"""
Jobs:
Job list curated below:
1.	Previous display jobs:
    1.	Move to window-relative rather than absolute units approach
    2.	Position grids using normalized, window-relative units
    3.	Specify stimuli in either pixels or visual angle approach
2.	Task jobs:
    1.	Tidy up spatial rotation task
        1. Restructure to use sensible parameter assumptions/passing
        2. There's a bug in the algorithm which needs fixing
    2.	Add the task-switching parameters
        1.	All stimuli are presented for 500 ms
        2.	Participants have 2000 ms to answer, before the next trial begins (nonanswered trials count as incorrect)
        3.	For now, each task should consist of 10 trials before switching
        4.	The “Next Task:__” cues are either 500 ms or 4000 ms
    3.	Add instruction slides
    4. SAVE the data!
        1. Save a CSV representation of the key variables
3.	Other
    1.	Content unit test
    2.	Package unit test
    3.	DRY
    4.	Reorder files
    5.	Add EEG/fMRI cues (Tibor is on it!)
    6.	Add an ability to quit the task midway. Tibor and I tried to exit early by pressing esc or exiting the screen, but it would not disappear unless we finished the task.

__________________________________________

"""
import taskSwitching as tS
from psychopy import visual
from random import shuffle
import enum


class TrialTypes(enum.Enum):
    DIGIT_SPAN = "Digit Span"
    SPATIAL_SPAN = "Spatial Span"
    SPATIAL_ROTATION = "Spatial Rotation"


class InfoCardDurations(enum.Enum):
    SHORT = .5
    LONG = 4


win = visual.Window(
    size=[800, 800],
    units="pix",
    fullscr=False,
    color=[0, 0, 0],
    gammaErrorPolicy="warn"
)

exp = tS.Experiment(window=win)

n = 5

stimuli = {
    "SpatialSpan": tS.get_spatial_span_stimuli(n),
    "DigitSpan": tS.get_digit_span_stimuli(n),
    "SpatialRotation": tS.get_spatial_rotation_stimuli(n)
}

# Define experiment
ic = [
    tS.ComponentInfoCard(
        experiment=exp,
        next_task=TrialTypes.SPATIAL_ROTATION.value,
        break_duration=InfoCardDurations.LONG.value
    )
]

ss = [
    tS.TrialSpatialSpan(
        trialNumber=i,
        experiment=exp,
        stimulus=stimuli["SpatialSpan"][i]
    ) for i in range(len(stimuli["SpatialSpan"]))
]

ds = [
    tS.TrialDigitSpan(
        trialNumber=i,
        experiment=exp,
        stimulus=stimuli["DigitSpan"][i]
    ) for i in range(len(stimuli["DigitSpan"]))
]

sr = [
    tS.TrialSpatialRotation(
        trialNumber=i,
        experiment=exp,
        stimulus=stimuli["SpatialRotation"][i]
    ) for i in range(len(stimuli["SpatialRotation"]))
]

# trials = ss + ds
trials = sr
shuffle(trials)
trials = ic + trials
trials.insert(n, tS.ComponentRest(break_duration=5, experiment=exp))

exp.trials = trials
# exp.trials = [
#     tS.Trial(
#         trial_number = 0,
#         experiment=exp,
#         stimulus=[tS.make_display_numbers(
#             rows=tS.np.repeat(list(range(4)), 4),
#             cols=tS.np.tile(list(range(4)), 4),
#             values=list(range(16)),
#             row_num=4, col_num=4
#         )],
#         stimulus_duration=5
#     )
# ]

exp.run()

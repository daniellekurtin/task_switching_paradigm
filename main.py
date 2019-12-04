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
from pyniexp import scannersynch
import enum


# Set some useful constants
class Config(enum.Enum):
    SYNCH_CONFIG = 'config.json'
    IN_SCANNER = False
    TR = 2 # seconds
    MIN_LOG_LEVEL = 'INFO'

class TrialTypes(enum.Enum):
    DIGIT_SPAN = "Digit Span"
    SPATIAL_SPAN = "Spatial Span"
    SPATIAL_ROTATION = "Spatial Rotation"


class InfoCardDurations(enum.Enum):
    SHORT = .5
    LONG = 4


class RunLength(enum.IntEnum):
    MIN = 15
    MAX = 21


class Block(enum.IntEnum):
    COUNT = 4
    LENGTH = 5
    TRIAL_COUNT = 144    # if this is not divisible by the number of task types things will go wrong
    BREAK_TIME = 120

if __name__ == '__main__':
    # Create the window we'll display the experiment in
    win = visual.Window(
        size=[800, 800],
        units="pix",
        fullscr=False,
        color=[0, 0, 0],
        gammaErrorPolicy="warn"
    )

    # Create interface for scanner pulse and respons box
    SSO = scannersynch.scanner_synch(config=Config.SYNCH_CONFIG.value,emul_synch=not(Config.IN_SCANNER.value),emul_buttons=not(Config.IN_SCANNER.value))
    SSO.set_synch_readout_time(0.5)
    SSO.TR = Config.TR.value

    SSO.set_buttonbox_readout_time(0.5)
    if not(SSO.emul_buttons): SSO.add_buttonbox('Nata')
    else: SSO.buttons = ['1','2','3'] 

    SSO.start_process()


    # Create the experiment object
    exp = tS.Experiment(window=win, synch=SSO, log_level=Config.MIN_LOG_LEVEL.value)

    # Create stimuli. Expect this whole process will eventually be wrapped into the Experiment class
    n = Block.TRIAL_COUNT * Block.COUNT / len(TrialTypes)

    stimuli = {
        "SpatialSpan": tS.get_spatial_span_stimuli(n),
        "DigitSpan": tS.get_digit_span_stimuli(n),
        "SpatialRotation": tS.get_spatial_rotation_stimuli(n)
    }

    # Define experimental trials using stimuli
    ss = [
        tS.TrialSpatialSpan(
            experiment=exp,
            stimulus=stimuli["SpatialSpan"][i]
        ) for i in range(len(stimuli["SpatialSpan"]))
    ]

    ds = [
        tS.TrialDigitSpan(
            experiment=exp,
            stimulus=stimuli["DigitSpan"][i]
        ) for i in range(len(stimuli["DigitSpan"]))
    ]

    sr = [
        tS.TrialSpatialRotation(
            experiment=exp,
            stimulus=stimuli["SpatialRotation"][i]
        ) for i in range(len(stimuli["SpatialRotation"]))
    ]

    # Currently these need to be in the same order as the magazines defined below.
    # This is risky and should be made more robust.
    ics = [
        tS.ComponentInfoCard(
            experiment=exp,
            next_task=TrialTypes.SPATIAL_SPAN.value
        ),
        tS.ComponentInfoCard(
            experiment=exp,
            next_task=TrialTypes.DIGIT_SPAN.value
        ),
        tS.ComponentInfoCard(
            experiment=exp,
            next_task=TrialTypes.SPATIAL_ROTATION.value
        )
    ]

    trials = []
    # Construct experimental trial order
    for b in range(Block.COUNT):          # Blocks
        # Stack up the trials into a queue by type
        magazines = [[], [], []]
        for i in range(int(Block.TRIAL_COUNT / len(TrialTypes))):
            magazines[0].insert(i, ss.pop())
            magazines[1].insert(i, ds.pop())
            magazines[2].insert(i, sr.pop())

        t = 0
        magazine = -1
        while t < Block.LENGTH:     # Trials

            # Create a new run of trials of a random length
            # Guard against too large a minimum run length (orphan trials)
            if max([len(m) for m in magazines]) < RunLength.MIN:
                run_length = max([len(m) for m in magazines])
            else:
                run_length = tS.randint(RunLength.MIN, RunLength.MAX)

            # Find a magazine with enough trials for the run_length
            n = 0
            while True:
                mag = tS.randint(0, len(magazines) - 1)
                if mag != magazine and len(magazines[mag]) >= run_length:
                    magazine = mag
                    break
                # Catch infinite loops
                n += 1
                if n > 10000:
                    raise RuntimeError

            # Create run
            # Random display time for Info Card
            if tS.randint(0, 1):
                d = InfoCardDurations.LONG.value
            else:
                d = InfoCardDurations.SHORT.value

            ic = tS.ComponentInfoCard(
                experiment=exp,
                next_task=ics[magazine].next_task,
                break_duration=d
            )

            trials.append(ic)

            # Pop trials from magazine into the block definition
            for r in range(run_length):     # Runs
                trials.append(magazines[magazine].pop())
                trials.append(tS.ComponentTrialGap(experiment=exp))

            t += run_length

        # Add a block break
        if b < Block.COUNT - 1:
            trials.append(tS.ComponentRest(experiment=exp, break_duration=Block.BREAK_TIME))

    # Load trials into the experiment
    exp.trials = trials

    # Run the experiment
    exp.synch.wait_for_synch()
    exp.run()

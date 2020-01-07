"""
Jobs:
1. Add a "press any key to begin" button
2. Hide countdown on breaks (which are now 2 minutes) until there is 5 seconds left.
Display jobs:
3. Create monitor, window
4. Specify panel size in degrees of visual arc (deg).
5. Specify components drawn on panel in percentages/standard units.
__________________________________________

"""
import taskSwitching as tS
from psychopy import visual
from pyniexp import scannersynch
import enum
import random
import math


# Set some useful constants
class Config(enum.Enum):
    SYNCH_CONFIG = '../config.json'
    IN_SCANNER = False
    TR = 2                          # seconds
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
    SWITCH_COUNT = 3
    # COUNT * SWITCH_COUNT must be divisible by the number of unique switch types * unique InfoCardDurations
    BREAK_TIME = 120


def get_run_sequence():
    """
    Produces a sequence of runs which ensures an equal number of transitions of each type.
    :return: list: TrialType sequence for the runs
    """

    # Calculate the number of switches between each kind of task (= n * (n-1))
    unique_switch_count = len(TrialTypes) * (len(TrialTypes) - 1)

    # Check we have the right number of switches and blocks to have equal numbers of each kind of switch
    if (Block.SWITCH_COUNT * Block.COUNT) % unique_switch_count != 0:
        raise ValueError("Total number of switches (" +
                         (Block.SWITCH_COUNT * Block.COUNT) +
                         ") must be divisible by number of unique switches (" +
                         unique_switch_count + ")")

    switch_count = int(Block.SWITCH_COUNT * Block.COUNT / unique_switch_count)

    # Build tallies for tracking each kind of switch
    # Addressed as switches[from][to] = switch_count
    switches = {}
    for tt in TrialTypes:
        s = {}
        for ot in TrialTypes:
            if ot == tt:
                continue
            s[ot] = switch_count

        switches[tt] = s

    # Add switches in a weighted random fashion until they're all assigned
    n = 0
    while True:
        n += 1
        try:
            # Attempt to construct a valid sequence
            s = tS.deepcopy(switches)
            sequence = [random.choice(list(TrialTypes))]
            while len(sequence) <= Block.SWITCH_COUNT * Block.COUNT:
                # Add a run of the next trial type
                f = sequence[len(sequence) - 1]  # TrialType we're switching from

                # Build a pool of choices for the next TrialType in the sequence
                choices = []
                for x in s[f]:
                    for i in range(s[f][x]):
                        choices.append(x)

                if len(choices) == 0:
                    raise RuntimeError

                t = random.choice(choices)  # Pick a TrialType from the pool to switch to
                sequence.append(t)

                s[f][t] -= 1  # record switch from f to t (take this switch out of the pool)

        except RuntimeError:
            pass

        # Check whether we have a valid solution
        if len(sequence) >= Block.SWITCH_COUNT * Block.COUNT:
            break
        elif n > 1000:
            raise RuntimeError("Exceeded maximum attempts to create a run sequence.")

    return sequence


def create_trial_by_type(trial_type, __prevent_recursion__=False, **kwargs):
    """
    Create a new trial
    :param trial_type: Type(s) of trial(s) to create
    :type trial_type: TrialTypes|TrialTypes[]
    :param __prevent_recursion__: prevent automatically expanding non-iterable type parameter
    :type __prevent_recursion__: bool
    :param kwargs: arguments handed to the trial creation functions
    :return:
    """
    out = []

    # Handle being fed a list of TrialTypes
    try:
        for t in trial_type:
            if not isinstance(t, TrialTypes):
                raise ValueError("trial_type must be a TrialType")

            if t == TrialTypes.DIGIT_SPAN:
                out.append(tS.TrialDigitSpan(**kwargs))
                break
            if t == TrialTypes.SPATIAL_SPAN:
                out.append(tS.TrialSpatialSpan(**kwargs))
                break
            if t == TrialTypes.SPATIAL_ROTATION:
                out.append(tS.TrialSpatialRotation(**kwargs))
                break

            raise ValueError("Unrecognised trial trial_type requested: " + t)

    except TypeError:
        if __prevent_recursion__:
            raise
        # If handed just one TrialType, wrap it as a list and return the first answer
        return create_trial_by_type([trial_type], __prevent_recursion__=True, **kwargs)[0]

    return out


def create_stimulus_by_type(trial_type, __prevent_recursion__=False, **kwargs):
    """
    Create a new stimulus
    :param trial_type: Type(s) of stimulus(i) to create
    :type trial_type: TrialTypes|TrialTypes[]
    :param __prevent_recursion__: prevent automatically expanding non-iterable type parameter
    :type __prevent_recursion__: bool
    :param kwargs: arguments handed to the stimulus creation functions
    :return: stimulus list for the desired trial types
    """
    out = []

    # Handle being fed a list of TrialTypes
    try:
        for t in trial_type:
            if not isinstance(t, TrialTypes):
                raise ValueError("trial_type must be a TrialType")

            if t == TrialTypes.DIGIT_SPAN:
                out.append(tS.get_digit_span_stimuli(n=1, **kwargs))
                break
            if t == TrialTypes.SPATIAL_SPAN:
                out.append(tS.get_spatial_span_stimuli(n=1, **kwargs))
                break
            if t == TrialTypes.SPATIAL_ROTATION:
                out.append(tS.get_spatial_rotation_stimuli(n=1, **kwargs))
                break

            raise ValueError("Unrecognised trial trial_type requested: " + t)

    except TypeError:
        if __prevent_recursion__:
            raise
        # If handed just one TrialType, wrap it as a list and return the first answer
        # Not sure why we're double-unwrapping, but it is necessary.
        return create_stimulus_by_type([trial_type], __prevent_recursion__=True, **kwargs)[0][0]

    return out


def trials_from_sequence(sequence, experiment):
    """
    Create a list of Trials given a sequence of TrialTypes.
    Each TrialType in the sequence specifies a run of trials divided over the experimental blocks.
    In general, Trials are preceeded by an Inter-Trial-Interval, and runs are preceeded by an indicator that there is a
    new trial type upcoming, displayed for a run intro period length.
    There are the following special rules:
    Blocks end and begin with half-length runs of the same trial type (i.e. block breaks happen in the middle of the
    last run), except for the first block which beings with a full-length run.
    There is no ITI before the first trial in a run (this is covered by the run intro period length).

    Overall, sequences should be balanced for switch counts, and should be long enough to balance switch counts for
    run intro period length (ripl) counts.

    :param sequence: a sequence of TrialTypes for consecutive runs
    :trial_type sequence: TrialTypes[]
    :param experiment: the Experiment to bind the Trials to
    :trial_type exp: tS.Experiment
    :return: tS.Trial[]
    """
    trials = []
    remainder = {"trial_type": None, "n": 0}

    # Calculate the number of switches between each kind of task
    unique_switch_count = len(TrialTypes) * (len(TrialTypes) - 1)
    unique_ripl_count = len(InfoCardDurations)  # run intro period lengths
    if (Block.SWITCH_COUNT * Block.COUNT) % (unique_switch_count * unique_ripl_count) != 0:
        raise ValueError("Total number of switches (" +
                         (Block.SWITCH_COUNT * Block.COUNT) +
                         ") must be divisible by number of unique switches * number of intro period lengths (" +
                         unique_switch_count + " * " + unique_ripl_count + " = " +
                         (unique_switch_count * unique_ripl_count) + ")")

    ripl_count = int(Block.SWITCH_COUNT * Block.COUNT / (unique_switch_count * unique_ripl_count))

    # Build tallies for tracking the number of switches of each trial_type with each run intro period length
    # Addressed as intro_lengths[from][to][introLength] = count
    intro_lengths = {}
    for tt in TrialTypes:
        s = {}
        for ot in TrialTypes:
            if ot == tt:
                continue
            s[ot] = {}
            for ripl in InfoCardDurations:
                s[ot][ripl] = ripl_count

        intro_lengths[tt] = s

    # Construct each block
    for b in range(Block.COUNT):

        last_block = b == Block.COUNT - 1

        # If there are trials left over from before the block break, add them here
        if remainder["n"] > 0:
            # Upcoming run trial_type notification
            trials.append(
                tS.ComponentInfoCard(
                    experiment=experiment,
                    next_task=remainder["trial_type"].value,
                    # At the beginning of a block use a random run intro period length
                    break_duration=random.choice(list(InfoCardDurations)).value
                )
            )
            # Remaining trials from before the block break
            for i in range(remainder["n"]):
                if i > 0:
                    trials.append(tS.ComponentTrialGap(experiment=experiment))
                trials.append(
                    create_trial_by_type(
                        remainder["trial_type"],
                        experiment=experiment,
                        stimulus=create_stimulus_by_type(remainder["trial_type"], experiment=experiment)
                    )
                )
        else:
            # First block in the experiment has a full run
            trial_type = sequence[0]
            run_length = random.randint(RunLength.MIN, RunLength.MAX)
            # Upcoming run trial_type notification
            trials.append(
                tS.ComponentInfoCard(
                    experiment=experiment,
                    next_task=trial_type.value,
                    # At the beginning of a block use a random run intro period length
                    break_duration=random.choice(list(InfoCardDurations)).value
                )
            )
            # Remaining trials from before the block break
            for i in range(run_length):
                if i > 0:
                    trials.append(tS.ComponentTrialGap(experiment=experiment))
                trials.append(
                    create_trial_by_type(
                        trial_type,
                        experiment=experiment,
                        stimulus=create_stimulus_by_type(trial_type, experiment=experiment)
                    )
                )

        # Construct each run
        for s in range(Block.SWITCH_COUNT):
            i = Block.SWITCH_COUNT * b + s + 1 # index of run in sequence
            trial_type = sequence[i]
            run_length = random.randint(RunLength.MIN, RunLength.MAX)
            end_of_block = s == Block.SWITCH_COUNT - 1

            # Pick from the ripls available (weighted random)
            choices = []
            ripls = intro_lengths[sequence[i - 1]][sequence[i]]
            for x in ripls:
                for r in range(ripls[x]):
                    choices.append(x)

            if len(choices) == 0:
                raise RuntimeError("No choices remaining for run intro period length")

            r = random.choice(choices)  # ripl selected

            intro_lengths[sequence[i - 1]][sequence[i]][r] -= 1  # decrement counter
            break_duration = r

            # Switch: add a run trial_type notification for upcoming trials
            trials.append(
                tS.ComponentInfoCard(
                    experiment=experiment,
                    next_task=trial_type.value,
                    break_duration=break_duration.value
                )
            )

            # Handle runs split by the end of the block
            if end_of_block:
                r = math.floor(run_length / 2)
                remainder["trial_type"] = trial_type
                remainder["n"] = run_length - r
                run_length = r

            # Add the actual trials themselves
            for i in range(run_length):
                if i > 0:
                    trials.append(tS.ComponentTrialGap(experiment=experiment))
                trials.append(
                    create_trial_by_type(
                        trial_type,
                        experiment=experiment,
                        stimulus=create_stimulus_by_type(trial_type, experiment=experiment)
                    )
                )

        if not last_block:
            # Block break
            trials.append(
                tS.ComponentRest(
                    experiment=experiment,
                    break_duration=Block.BREAK_TIME)
            )
        else:
            # We can append the end-of-experiment feedback if we make it here.
            pass

    return trials


if __name__ == '__main__':

    # Create the window we'll display the experiment in
    win = visual.Window(
        size=[800, 800],
        units="pix",
        fullscr=False,
        color=[0, 0, 0],
        gammaErrorPolicy="warn"
    )

    # Create interface for scanner pulse and response box
    SSO = scannersynch.scanner_synch(
        config=Config.SYNCH_CONFIG.value,
        emul_synch=not Config.IN_SCANNER.value,
        emul_buttons=not Config.IN_SCANNER.value
    )
    SSO.set_synch_readout_time(0.5)
    SSO.TR = Config.TR.value

    SSO.set_buttonbox_readout_time(0.5)
    if not SSO.emul_buttons:
        SSO.add_buttonbox('Nata')
    else:
        SSO.buttons = ['1', '2', '3']

    SSO.start_process()

    # Create the experiment object
    exp = tS.Experiment(
        window=win,
        synch=SSO,
        log_level=Config.MIN_LOG_LEVEL.value
    )

    seq = get_run_sequence()
    trials = trials_from_sequence(seq, experiment=exp)

    # Debugging
    n = 0
    for i in range(len(trials)):
        t = trials[i]

        if t.__class__.__name__ == "ComponentTrialGap":
            continue

        if isinstance(t, tS.ComponentInfoCard):
            if n > 0:
                print("> " + str(n) + " x " + str(tt))
            print(t.__class__.__name__)
            n = 0
        elif isinstance(t, tS.ComponentRest):
            print("> " + str(n) + " x " + str(tt))
            print("----------Block Break------------")
            n = 0
        else:
            n += 1
            tt = t.__class__.__name__

    # print the final trial type
    print("> " + str(n) + " x " + str(tt))

    # Load trials into the experiment
    exp.trials = trials

    # Run the experiment
    exp.synch.wait_for_synch()
    exp.run()
    
    exp = None
    SSO = None

import taskSwitching as tS
from copy import deepcopy
from os import getcwd, path, makedirs
import enum
import random
import math
import csv
import numpy as np
import pandas as pd


class ExperimentTaskSwitch(tS.Experiment):
    """
    The ExperimentTaskSwitch helps with the basic setup of a task switching experiment.
    """
    class TrialTypes(enum.Enum):
        DIGIT_SPAN = "Digit Span"
        SPATIAL_SPAN = "Spatial Span"
        SPATIAL_ROTATION = "Spatial Rotation"

    stimulus_durations = {
        TrialTypes.DIGIT_SPAN: 0.25,
        TrialTypes.SPATIAL_SPAN: 0.5,
        TrialTypes.SPATIAL_ROTATION: 0.5
    }

    class InfoCardDurations(enum.Enum):
        SHORT = .5
        LONG = 4

    class RunLength(enum.IntEnum):
        MIN = 6
        MAX = 9

    class Block(enum.IntEnum):
        COUNT = 4
        SWITCH_COUNT = 9
        # COUNT * SWITCH_COUNT must be divisible by the number of unique switch types * unique InfoCardDurations
        BREAK_TIME = 120

    run_sequence = None

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        for k in kwargs.keys():
            self.__setattr__(k, kwargs[k])

        if self.run_sequence is None:
            self.run_sequence = self.get_run_sequence()
        if len(self.trials) == 0:
            # incorporate "press any key to begin"
            info = [tS.ComponentStart(experiment=self)]
            self.trials = info + self.trials_from_sequence(self.run_sequence)

    def get_run_sequence(self):
        """
        Produces a sequence of runs which ensures an equal number of transitions of each type.
        :return: list: TrialType sequence for the runs
        """

        # Calculate the number of switches between each kind of task (= n * (n-1))
        unique_switch_count = len(self.TrialTypes) * (len(self.TrialTypes) - 1)

        # Check we have the right number of switches and blocks to have equal numbers of each kind of switch
        if (self.Block.SWITCH_COUNT * self.Block.COUNT) % unique_switch_count != 0:
            raise ValueError("Total number of switches (" +
                             str(self.Block.SWITCH_COUNT * self.Block.COUNT) +
                             ") must be divisible by number of unique switches (" +
                             str(unique_switch_count) + ")")

        switch_count = int(self.Block.SWITCH_COUNT * self.Block.COUNT / unique_switch_count)

        # Build tallies for tracking each kind of switch
        # Addressed as switches[from][to] = switch_count
        switches = {}
        for tt in self.TrialTypes:
            s = {}
            for ot in self.TrialTypes:
                if ot == tt:
                    continue
                s[ot] = switch_count

            switches[tt] = s

        # Add switches in a weighted random fashion until they're all assigned
        n = 0
        while True:
            n += 1
            sequence = []
            try:
                # Attempt to construct a valid sequence
                s = deepcopy(switches)
                sequence = [random.choice(list(self.TrialTypes))]
                while len(sequence) <= self.Block.SWITCH_COUNT * self.Block.COUNT:
                    if hasattr(self, "loading_text_stim") and self.loading_text_stim is not None:
                        self.loading_text_stim.text = "Generating run sequence... [attempt " + str(n + 1) + "] " + \
                                            str(len(sequence)) + "/" + str(self.Block.COUNT * self.Block.SWITCH_COUNT)
                        self.loading_text_stim.draw()
                        self.window.flip()
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
            if len(sequence) >= self.Block.SWITCH_COUNT * self.Block.COUNT:
                break
            elif n > 1000:
                if self.loading_text_stim is not None:
                    self.loading_text_stim.text = "Failed to generate run sequence: maximum iterations exceeded!"
                    self.loading_text_stim.color = [1, -1, -1]
                    self.loading_text_stim.draw()
                    self.window.flip()
                raise RuntimeError("Exceeded maximum attempts to create a run sequence.")

        return sequence

    def create_trial_by_type(self, trial_type, __prevent_recursion__=False, **kwargs):
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
                if not isinstance(t, self.TrialTypes):
                    raise ValueError("trial_type must be a TrialType")

                if t == self.TrialTypes.DIGIT_SPAN:
                    out.append(tS.TrialDigitSpan(trial_type=t, **kwargs))
                    break
                if t == self.TrialTypes.SPATIAL_SPAN:
                    out.append(tS.TrialSpatialSpan(trial_type=t, **kwargs))
                    break
                if t == self.TrialTypes.SPATIAL_ROTATION:
                    out.append(tS.TrialSpatialRotation(trial_type=t, **kwargs))
                    break

                raise ValueError("Unrecognised trial trial_type requested: " + str(t.value))

        except TypeError:
            if __prevent_recursion__:
                raise
            # If handed just one TrialType, wrap it as a list and return the first answer
            return self.create_trial_by_type([trial_type], __prevent_recursion__=True, **kwargs)[0]

        return out

    def create_stimulus_by_type(self, trial_type, __prevent_recursion__=False, **kwargs):
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
                if not isinstance(t, self.TrialTypes):
                    raise ValueError("trial_type must be a TrialType")

                if t == self.TrialTypes.DIGIT_SPAN:
                    out.append(tS.get_digit_span_stimuli(n=1, **kwargs))
                    break
                if t == self.TrialTypes.SPATIAL_SPAN:
                    out.append(tS.get_spatial_span_stimuli(n=1, **kwargs))
                    break
                if t == self.TrialTypes.SPATIAL_ROTATION:
                    out.append(tS.get_spatial_rotation_stimuli(n=1, **kwargs))
                    break

                raise ValueError("Unrecognised trial trial_type requested: " + t)

        except TypeError:
            if __prevent_recursion__:
                raise
            # If handed just one TrialType, wrap it as a list and return the first answer
            # Not sure why we're double-unwrapping, but it is necessary.
            return self.create_stimulus_by_type([trial_type], __prevent_recursion__=True, **kwargs)[0][0]

        return out

    def trials_from_sequence(self, sequence):
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
        :return: tS.Trial[]
        """
        trials = []
        remainder = {"trial_type": None, "n": 0}

        # Calculate the number of switches between each kind of task
        unique_switch_count = len(self.TrialTypes) * (len(self.TrialTypes) - 1)
        unique_ripl_count = len(self.InfoCardDurations)  # run intro period lengths
        if (self.Block.SWITCH_COUNT * self.Block.COUNT) % (unique_switch_count * unique_ripl_count) != 0:
            raise ValueError("Total number of switches (" +
                             str(self.Block.SWITCH_COUNT * self.Block.COUNT) +
                             ") must be divisible by number of unique switches * number of intro period lengths (" +
                             str(unique_switch_count) + " * " + str(unique_ripl_count) + " = " +
                             str(unique_switch_count * unique_ripl_count) + ")")

        ripl_count = int(self.Block.SWITCH_COUNT * self.Block.COUNT / (unique_switch_count * unique_ripl_count))

        # Build tallies for tracking the number of switches of each trial_type with each run intro period length
        # Addressed as intro_lengths[from][to][introLength] = count
        intro_lengths = {}
        for tt in self.TrialTypes:
            s = {}
            for ot in self.TrialTypes:
                if ot == tt:
                    continue
                s[ot] = {}
                for ripl in self.InfoCardDurations:
                    s[ot][ripl] = ripl_count

            intro_lengths[tt] = s

        # Construct each block
        for b in range(self.Block.COUNT):

            last_block = b == self.Block.COUNT - 1

            # If there are trials left over from before the block break, add them here
            if remainder["n"] > 0:
                # Upcoming run trial_type notification
                trials.append(
                    tS.ComponentInfoCard(
                        experiment=self,
                        next_task=remainder["trial_type"].value,
                        # At the beginning of a block use a random run intro period length
                        break_duration=random.choice(list(self.InfoCardDurations)).value
                    )
                )
                # Remaining trials from before the block break
                for i in range(remainder["n"]):
                    if i > 0:
                        trials.append(tS.ComponentTrialGap(experiment=self))
                    trials.append(
                        self.create_trial_by_type(
                            remainder["trial_type"],
                            experiment=self,
                            stimulus=self.create_stimulus_by_type(remainder["trial_type"], experiment=self)
                        )
                    )
            else:
                # First block in the experiment has a full run
                trial_type = sequence[0]
                run_length = random.randint(self.RunLength.MIN, self.RunLength.MAX)
                # Upcoming run trial_type notification
                trials.append(
                    tS.ComponentInfoCard(
                        experiment=self,
                        next_task=trial_type.value,
                        # At the beginning of a block use a random run intro period length
                        break_duration=random.choice(list(self.InfoCardDurations)).value
                    )
                )
                # Remaining trials from before the block break
                for i in range(run_length):
                    if i > 0:
                        trials.append(tS.ComponentTrialGap(experiment=self))
                    trials.append(
                        self.create_trial_by_type(
                            trial_type,
                            experiment=self,
                            stimulus=self.create_stimulus_by_type(trial_type, experiment=self)
                        )
                    )

            # Construct each run
            for s in range(self.Block.SWITCH_COUNT):

                if hasattr(self, "loading_text_stim") and self.loading_text_stim is not None:
                    self.loading_text_stim.text = "Generating trials for block " + str(b + 1) + "/" + \
                                        str(self.Block.COUNT.value) + ": " + \
                                        str(round(s / self.Block.SWITCH_COUNT.value * 100)) + "%"
                    self.loading_text_stim.draw()
                    self.window.flip()

                i = self.Block.SWITCH_COUNT * b + s + 1  # index of run in sequence
                trial_type = sequence[i]
                run_length = random.randint(self.RunLength.MIN, self.RunLength.MAX)
                end_of_block = s == self.Block.SWITCH_COUNT - 1

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
                        experiment=self,
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
                        trials.append(tS.ComponentTrialGap(experiment=self))
                    trials.append(
                        self.create_trial_by_type(
                            trial_type,
                            experiment=self,
                            stimulus=self.create_stimulus_by_type(trial_type, experiment=self)
                        )
                    )

            if not last_block:
                # Block break
                trials.append(
                    tS.ComponentRest(
                        experiment=self,
                        break_duration=self.Block.BREAK_TIME)
                )
            else:
                # We can append the end-of-experiment feedback if we make it here.
                pass

        return trials

    def trial_order_to_string(self, newline=''):
        n = 0
        lines = []
        
        for i in range(len(self.trials)):
            t = self.trials[i]

            if t.__class__.__name__ == "ComponentTrialGap" or t.__class__.__name__ == "ComponentStart":
                continue

            if isinstance(t, tS.ComponentInfoCard):
                if n > 0:
                    lines.append(str(t.break_duration))
                    lines.append("> " + str(n) + " x " + str(tt))
                lines.append(t.__class__.__name__)
                n = 0
            elif isinstance(t, tS.ComponentRest):
                lines.append("> " + str(n) + " x " + str(tt))
                lines.append("Block Break")
                n = 0
            else:
                n += 1
                tt = t.__class__.__name__
        
        return lines

    def debug_trial_order(self):
        for s in self.trial_order_to_string():
            print(s + "\n")

    def save_trial_order(self, public=True):
        
        if public:
            access = "public"
        else:
            access = "private"
        file_name = path.join(self.save_path, access, self.participant.id + "_" + "task_structure" + "_" + self.version + ".txt")
        
        # self.save_path2 = (r'C:\Users\danie\Documents\SURREY\Project_1\task_switching_paradigm\data\public\TaskStructure')
        # file_name = path.join(self.save_path2, self.participant.id + "_" + "task_structure" + "_" + self.version + ".txt")
        
        with open(file_name, 'w+', newline='') as w:
            for s in self.trial_order_to_string():
                w.write("\n" + s)


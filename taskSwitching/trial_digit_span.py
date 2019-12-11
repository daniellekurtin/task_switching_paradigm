from taskSwitching.trial import *
from copy import deepcopy


def get_digit_span_stimuli(n, experiment, span=None, allow_repeats=False, row=None, col=None):
    """
    Generate digit span stimuli
    :param n: number of stimuli to produce
    :param experiment: Experiment to attach to
    :type experiment: Experiment
    :param span: number of digits in each stimulus, by default the Experiment.grid_size
    :type span: int|None
    :param allow_repeats: whether digits can appear multiple times
    :type allow_repeats: bool
    :param col: override random column choice
    :type col: int[]
    :param row: override random row choice
    :type row: int[]
    :return: n stimulus nparrays
    """
    if span is None:
        span = experiment.grid_size

    if span > 10 and not allow_repeats:
        raise ValueError('Not possible to produce non-repeating sequences of digits with length > 10')

    values = []
    if row is None:
        rows = []
    else:
        rows = row
    if col is None:
        cols = []
    else:
        cols = col

    while len(values) < n:
        v = [randint(0, 9)]
        while len(v) < span:
            r = randint(0, 9)
            if allow_repeats or r not in v:
                v.append(r)

        if v not in values:
            values.append(v)
            if row is None:
                rows.append(randint(0, experiment.grid_size - 1))
            if col is None:
                cols.append(randint(0, experiment.grid_size - 1))

    stimuli = []
    for i in range(len(values)):
        stimuli.append([
            make_display_numbers(
                rows=[rows[i]],
                cols=[cols[i]],
                values=[v],
                row_num=experiment.grid_size,
                col_num=experiment.grid_size
            ) for v in values[i]
        ])

    return stimuli


# Expects:
# stimulus {int[]} digits to display sequentially
# stimulus_duration {float} seconds to display each digit
class TrialDigitSpan(Trial):
    def __init__(self, **kwargs):
        """
        :param kwargs:
        """
        super().__init__(**kwargs)

    def prepare_answers(self, override_existing=False):
        if not (None in self.answers) and not override_existing:
            return

        # Find the cell which has the value in it at each time point
        dim = np.shape(self.stimulus[0])
        n_rows = dim[0]
        n_cols = dim[1]
        values = self.stimulus[0]
        values = np.reshape(values, (1, np.prod(np.shape(values))))
        values = values[0]
        indices = np.where([values[i] is not None for i in range(int(np.prod(np.shape(values))))])
        indices = int(indices[0])  # only one answer!

        values = self.stimulus
        values = [np.reshape(stim, (1, np.prod(np.shape(stim)))) for stim in values]
        values = [stim[0, indices] for stim in values]
        row = randint(0, n_rows - 1)

        answer = make_display_numbers(
            rows=[row] * len(self.stimulus),
            cols=[i for i in range(len(self.stimulus))],
            values=values,
            row_num=n_rows,
            col_num=n_cols
        )

        options = [answer]
        change_index = randint(0, len(values) - 1)
        allow_repeats = len(np.unique(values)) != len(values)

        while len(options) < 3:
            mutant = deepcopy(values)
            while mutant == values:
                mutant[change_index] = randint(0, 9)

                # go around again if there's a repeat
                if not allow_repeats:
                    if len(np.unique(mutant)) != len(mutant):
                        mutant = deepcopy(values)

            foil = make_display_numbers(
                rows=[row] * len(self.stimulus),
                cols=[i for i in range(len(self.stimulus))],
                values=mutant,
                row_num=n_rows,
                col_num=n_cols
            )

            if not any([np.array_equal(foil, o) for o in options]):
                options.append(foil)

        shuffle(options)
        self.answer_index = np.where([np.array_equal(answer, o) for o in options])
        self.answer_index = self.answer_index[0][0]
        self.answers = options

        self.log('Target answer = ' + str(self.answer_index))

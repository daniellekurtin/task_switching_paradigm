from src.taskSwitching.trial import *
from copy import deepcopy


def get_digit_span_stimuli(n, n_rows=4, n_cols=4, span=4, allow_repeats=False, row=None, col=None):
    """
    Generate digit span stimuli
    :param n: number of stimuli to produce
    :type n: int
    :param n_cols: max column number for random calculation
    :type n_cols: int
    :param n_rows: max row number for random calculation
    :type n_rows: int
    :param span: number of digits in each stimulus
    :type span: int
    :param allow_repeats: whether digits can appear multiple times
    :type allow_repeats: bool
    :param col: override random column choice
    :type col: int[]
    :param row: override random row choice
    :type row: int[]
    :return: n stimulus nparrays
    """
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
                rows.append(randint(0, n_rows - 1))
            if col is None:
                cols.append(randint(0, n_cols - 1))

    stimuli = []
    for i in range(len(values)):
        stimuli.append([
            make_display_numbers(
                rows=[rows[i]],
                cols=[cols[i]],
                values=[v],
                row_num=n_rows,
                col_num=n_cols
            ) for v in values[i]
        ])

    return stimuli


# Expects:
# stimulus {int[]} digits to display sequentially
# stimulusDuration {float} seconds to display each digit
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
        values = np.reshape(values, (len(values), np.prod(np.shape(values[0]))))

        answer = make_display_numbers(
            rows=[1] * len(self.stimulus),
            cols=[i for i in range(len(self.stimulus))],
            values=[stim[indices] for stim in values],
            row_num=n_rows,
            col_num=n_cols
        )

        values = [stim[indices] for stim in values]

        options = [answer]
        change_index = randint(0, len(values) - 1)
        allow_repeats = len(np.unique(values)) == len(values)

        while len(options) < 3:
            mutant = deepcopy(values)
            while mutant == values:
                mutant[change_index] = randint(0, 9)

                # go around again if there's a repeat
                if not allow_repeats and not len(np.unique(mutant)) == len(mutant):
                    mutant = values

            foil = make_display_numbers(
                rows=[1] * len(self.stimulus),
                cols=[i for i in range(len(self.stimulus))],
                values=[mutant[i] for i in range(4)],
                row_num=n_rows,
                col_num=n_cols
            )

            if not any([np.array_equal(foil, o) for o in options]):
                options.append(foil)

        shuffle(options)
        self.answerIndex = np.where([np.array_equal(answer, o) for o in options])
        self.answerIndex = self.answerIndex[0][0]
        self.answers = options

        self.log('Target answer = ' + str(self.answerIndex))

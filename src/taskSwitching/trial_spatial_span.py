from src.taskSwitching.trial import *


def get_spatial_span_stimuli(n, n_rows=4, n_cols=4, span=4, numeral=None):
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
    :param numeral: number to display in the various positions
    :type numeral: int
    :return: n stimulus nparrays
    """
    if span > n_rows * n_cols:
        raise ValueError('Not possible to produce spatial span greater than number of cells')

    stimuli = []
    while len(stimuli) < n:
        rows = []
        cols = []
        hashes = []
        while len(rows) < span:
            row = randint(0, n_rows - 1)
            col = randint(0, n_cols - 1)

            # We can hash row and column together to quickly check for clashes
            h = hash((row, col))

            if h not in hashes:
                rows.append(row)
                cols.append(col)
                hashes.append(h)

        if numeral is None:
            v = randint(0, 9)
        else:
            v = numeral

        stimulus = {
            "rows": rows,
            "cols": cols,
            "numerals": [v] * len(rows)
        }

        if stimulus not in stimuli:
            stimuli.append(stimulus)

    output = []
    for s in stimuli:
        output.append([
            make_display_numbers(
                rows=[s["rows"][i]],
                cols=[s["cols"][i]],
                values=[s["numerals"][i]],
                row_num=n_rows,
                col_num=n_cols
            ) for i in range(len(s["rows"]))
        ])

    return output


class TrialSpatialSpan(Trial):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def prepare_answers(self, override_existing=False):
        if not (None in self.answers) and not override_existing:
            return

        # Find the cell which has the value in it at each time point
        rows = []
        cols = []
        numerals = []
        for s in self.stimulus:
            dim = np.shape(s)
            n_rows = dim[0]
            n_cols = dim[1]
            values = s
            values = np.reshape(values, (1, np.prod(np.shape(values))))
            values = values[0]
            indices = np.where([values[i] is not None for i in range(int(np.prod(np.shape(values))))])
            indices = int(indices[0])  # only one answer!

            values = s
            values = np.reshape(values, (1, np.prod(np.shape(s))))

            rows.append(floor(indices / n_cols))
            cols.append(indices % n_cols)
            numerals.append(values[0][indices])

        answer = make_display_numbers(
            rows=rows,
            cols=cols,
            values=numerals,
            row_num=n_rows,
            col_num=n_cols
        )
        options = [answer]
        ans_rows, ans_cols = np.where(answer!=None) 
        while len(options) < len(self.answers):
            # store all corrdinates that belong to the answe
            hashes = [hash((r, c)) for r, c in zip(rows, cols)]
            # drop a random corrdinate
            i_drop = randint(0, len(rows) - 1)
            rows = list(np.delete(ans_rows, i_drop))  
            cols = list(np.delete(ans_cols, i_drop))
            while len(rows) < n_rows:
                r = randint(0, n_rows - 1)
                c = randint(0, n_cols - 1)
                h = hash((r, c))
                if h not in hashes:
                    hashes.append(h)
                    rows.append(r)
                    cols.append(c)

            foil = make_display_numbers(
                rows=rows,
                cols=cols,
                values=numerals,
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

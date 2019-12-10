from taskSwitching.trial import *
from copy import deepcopy
import math


def get_spatial_rotation_stimuli(n, experiment, size=None, numeral=None):
    """
    Generate digit span stimuli
    :param n: number of stimuli to produce
    :type n: int
    :param experiment: Experiment to attach to
    :type experiment: Experiment
    :param size: number of digits in each stimulus, by default the Experiment.grid size
    :type size: int|None
    :param numeral: number to display in the various positions
    :type numeral: int
    :return: n stimulus nparrays
    """
    if size is None:
        size = experiment.grid_size

    if size > experiment.grid_size ** 2:
        raise ValueError('Not possible to produce spatial rotation shape larger than number of cells')

    stimuli = []
    while len(stimuli) < n:
        rows = []
        cols = []
        hashes = []
        # Keep track of previously used values because these stimuli build iteratively over presentations
        old_values = {
            "rows": [],
            "cols": []
        }
        while len(rows) < size:
            row = randint(0, experiment.grid_size - 1)
            col = randint(0, experiment.grid_size - 1)

            # We can hash row and column together to quickly check for clashes
            h = hash((row, col))

            if h not in hashes:
                old_values["rows"].append(row)
                old_values["cols"].append(col)
                rows.append(deepcopy(old_values["rows"]))
                cols.append(deepcopy(old_values["cols"]))
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
            append = True
            # Check the final stimulus iteration for rotational symmetry
            check = np.array([
                stimulus["rows"][len(stimulus["rows"]) - 1],
                stimulus["cols"][len(stimulus["cols"]) - 1]
            ])
            for deg in [90, 180, 270]:
                if np.all((np.equal(check, rotate(check, experiment.grid_size, deg)))):
                    append = False
                    break

            if append:
                stimuli.append(stimulus)

    output = []
    for s in stimuli:
        output.append([
            make_display_numbers(
                rows=[s["rows"][i]],
                cols=[s["cols"][i]],
                values=[s["numerals"][i]],
                row_num=experiment.grid_size,
                col_num=experiment.grid_size
            ) for i in range(len(s["rows"]))
        ])

    return output


def rotate(matrix, grid_size, deg=90):
    """
    Rotate an n x n grid clockwise.
    For a 90 degree clockwise rotation each cell (r, c) gets new coordinates (c, (n-1) - r).
    :param matrix: matrix of coordinates to manipulate
    :type matrix: nparray
    :param grid_size: number of cells in the grid
    :param deg: degrees to rotate, only steps of 90 will work
    :type deg: int
    :return: new matrix with rotated coordinates
    """

    if deg % 90 != 0:
        raise ValueError("rotate() only supports rotations of 90 degrees")

    # Recursively call rotate() to rotate by 90deg until we're 90deg away from target rotation
    # It would technically be more efficient to do this as a yielding iterative, but we'll stick with this for now
    if deg > 90:
        matrix = rotate(matrix, grid_size, deg - 90)

    new_matrix = np.zeros_like(matrix)

    # New row <- old column
    new_matrix[0] = matrix[1]
    # New column <- (n - 1) - old row
    new_matrix[1] = (grid_size - 1) - matrix[0]

    # reshape the matrix back to the form of the input
    return new_matrix.astype(int)


class TrialSpatialRotation(Trial):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def prepare_answers(self, override_existing=False):
        if not (None in self.answers) and not override_existing:
            return

        # Find the target numeral
        rows = []
        cols = []
        numerals = []

        dim = np.shape(self.stimulus)
        n_rows = dim[0]
        n_cols = dim[1]
        values = self.stimulus[len(self.stimulus) - 1]
        values = np.reshape(values, (1, np.prod(np.shape(values))))
        values = values[0]

        for i in range(len(values)):
            if values[i] is not None:
                numerals.append(values[i])
                rows.append(floor(i / n_cols))
                cols.append(i % n_cols)

        rotated = rotate(
            np.array([rows, cols]),
            n_rows
        )

        answer = make_display_numbers(
            rows=rotated[0, :],
            cols=rotated[1, :],
            values=numerals,
            row_num=n_rows,
            col_num=n_cols
        )
        options = [answer]
        ans_rows, ans_cols = np.where(np.invert(np.equal(answer, None)))
        hashes = [hash((r, c)) for r, c in zip(ans_rows, ans_cols)]
        mutate_index = randint(0, len(ans_rows) - 1)
        while len(options) < len(self.answers):
            # store all coordinates that belong to the answer
            # then drop the coordinate specified by mutate_at
            rows = list(np.delete(ans_rows, mutate_index))
            cols = list(np.delete(ans_cols, mutate_index))
            while len(rows) < n_rows:
                r = randint(0, n_rows - 1)
                c = randint(0, n_cols - 1)
                h = hash((r, c))
                if h not in hashes:
                    hashes.append(h)
                    rows.append(r)
                    cols.append(c)

            # Check we haven't accidentally made a rotation of the original stimulus
            okay = True
            check = np.array([rows, cols])
            for deg in [90, 180]:  # 270 covered already by the correct answer
                if np.all(np.equal(check, rotate(check, n_rows, deg))):
                    okay = False
                    break

            if okay:
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
        self.answer_index = np.where([np.array_equal(answer, o) for o in options])
        self.answer_index = self.answer_index[0][0]
        self.answers = options

        self.log('Target answer = ' + str(self.answer_index))

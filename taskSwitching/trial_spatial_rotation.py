from taskSwitching.trial import *
from copy import deepcopy
import math


def get_spatial_rotation_stimuli(n, n_rows=4, n_cols=4, size=4, numeral=None):
    """
    Generate digit span stimuli
    :param n: number of stimuli to produce
    :type n: int
    :param n_cols: max column number for random calculation
    :type n_cols: int
    :param n_rows: max row number for random calculation
    :type n_rows: int
    :param size: number of digits in each stimulus
    :type size: int
    :param numeral: number to display in the various positions
    :type numeral: int
    :return: n stimulus nparrays
    """
    if size > n_rows * n_cols:
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
            row = randint(0, n_rows - 1)
            col = randint(0, n_cols - 1)

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
                if np.all((np.equal(check, translate_and_rotate(check, deg)))):
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
                row_num=n_rows,
                col_num=n_cols
            ) for i in range(len(s["rows"]))
        ])

    return output


def translate_and_rotate(matrix, rotate_deg=90, translation_vector=None):
    """
    :param matrix: matrix to manipulate
    :type matrix: nparray
    :param rotate_deg: number of degrees to rotate anticlockwise
    :type rotate_deg: int
    :param translation_vector: 3x3 matrix containing the translation to prepend to the rotation and to invert
    afterwards, default (-2, -2)
    :type translation_vector: nparray|None
    :return: new matrix resulting from translating, rotating, and then anti-translating the original matrix
    """
    radians = math.radians(rotate_deg)

    if translation_vector is None:
        translation_vector = np.array([
            [-1.5],  # (n_row - 1) / 2
            [-1.5],  # (n_col - 1) / 2
            [0]
        ])

    rotation_matrix = np.array([
        [math.cos(radians), -math.sin(radians), 0],
        [math.sin(radians), math.cos(radians), 0],
        [0, 0, 1]
    ])

    if np.size(matrix, 0) == 2:
        matrix = np.vstack((
            matrix,
            np.repeat(1, np.size(matrix, 1))
        ))
        trim = True
    else:
        trim = False

    new_matrix = np.add(translation_vector, matrix)
    new_matrix = np.dot(rotation_matrix, new_matrix)
    new_matrix = np.add(translation_vector * -1, new_matrix)  # translate back

    # reshape the matrix back to the form of the input
    if trim:
        new_matrix = new_matrix[[0, 1], :]

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

        rotated = translate_and_rotate(
            np.array([rows, cols])
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
                if np.all(np.equal(check, translate_and_rotate(check, deg))):
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

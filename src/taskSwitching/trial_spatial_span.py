from src.taskSwitching.trial import *


class TrialSpatialSpan(Trial):
    def __init__(self, **kwargs):
        super().__init__(kwargs)

    def prepare_answers(self, override_existing=False):
        if hasattr(self, "answers") and not override_existing:
            return self.answers

        n_rows = self.stimulus.size[0]
        n_cols = self.stimulus.size[1]
        values = self.stimulus
        np.reshape(values, (1, np.prod(values.size)))
        values = values[0]
        indices = np.where(values is not None)

        answer = make_display_numbers(
            rows=[floor(i / n_cols) for i in indices],
            cols=[i % n_cols for i in indices],
            values=values,
            row_num=n_rows,
            col_num=n_cols
        )
        # foils = [make_display_numbers() for i in range(2)]
        # foils.append(answer)
        # shuffle(foils)
        #
        self.answers = answer

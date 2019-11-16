from src.taskSwitching.trial import *


# Expects:
# stimulus {int[]} digits to display sequentially
# stimulusDuration {float} seconds to display each digit
class TrialDigitSpan(Trial):
    def __init__(self, **kwargs):
        """
        :param kwargs:
        """
        super().__init__(**kwargs)

    def run(self):
        self.trial_gap()
        self.prepare()
        self.show_stimulus()
        self.collect_response()
        self.cleanup()

    def trial_gap(self):
        clock.wait(1)

    def prepare(self):
        self.prepare_answers()

        self.win.flip()
        self.log('Preparation complete for ' + str(self))
        clock.wait(.5)
        pass

    def show_stimulus(self):
        for n in self.stimulus:
            self.draw_number(n)
            clock.wait(self.stimulusDuration)

            self.grid.draw()
            self.win.flip()
            clock.wait(.5)

    def collect_response(self):
        # PsychoPy click response stuff?
        self.draw_answer_grids()
        self.win.flip()

        clock.wait(1)

        response = self.get_mouse_input()
        self.log('Answer = ' + str(response["answer"]))
        self.log('Mouse position = ' + str(response["position"]))

        if response["answer"] == self.answerIndex:
            self.log('CORRECT!')
        else:
            self.log('WRONG!')

    def cleanup(self):
        print("\n".join(self.logEntries))

    def draw_number(self, n):
        self.grid.draw()
        self.draw_stim(n)
        self.win.flip()

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

        options = [answer]
        while len(options) < 3:
            values = list(range(10))
            shuffle(values)

            foil = make_display_numbers(
                rows=[1] * len(self.stimulus),
                cols=[i for i in range(len(self.stimulus))],
                values=[values[i] for i in range(4)],
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

    def get_answer_grid_positions(self):
        n = len(self.answers)
        return [(
            self.win.size[0] / 2 - (self.grid.width + 1) * self.answerRectWidth,
            self.win.size[1] / 2 - (self.grid.height + 1) * self.answerRectHeight - self.win.size[1] * i / n
        ) for i in range(n)]

    def get_answer_grids(self):
        positions = self.get_answer_grid_positions()
        return [
            Grid(
                width_in_cells=4,
                height_in_cells=4,
                # including the rectangles we'll be using as cells
                psychopy_rect=visual.Rect(
                    win=self.win,
                    width=self.answerRectWidth,
                    height=self.answerRectHeight,
                    fillColor=[1, 1, 1],
                    lineColor=[-1, -1, -1]
                ),
                start_pos_tuple=positions[i]
            ) for i in range(len(self.answers))
        ]

    def draw_answer_grids(self):
        grids = self.get_answer_grids()
        for i in range(len(self.answers)):
            g = grids[i]
            g.draw()

            # Draw the purported answer over this grid
            self.draw_stim(self.answers[i], grid=g)

    def get_mouse_input(self):
        grids = self.get_answer_grids()
        my_mouse = event.Mouse(visible=True, win=self.win)
        event.clearEvents()  # get rid of other, unprocessed events
        while True:
            buttons, times = my_mouse.getPressed(getTime=True)

            if not buttons[0]:
                my_mouse.clickReset()
                continue

            pos = my_mouse.getPos()

            for a in range(len(grids)):
                g = grids[a]
                # check click is in the boundaries of the rectangle
                if g.click_is_in(pos):
                    return {
                        "time": times,
                        "position": pos,
                        "answer": a
                    }

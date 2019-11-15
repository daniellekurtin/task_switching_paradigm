from random import randint, shuffle
from itertools import combinations

# number = randint(1, 9)
grid_size = 3
n_filled = 2

def get_coordinates(n_filled, grid_size):
    out_corrd = []
    while len(out_corrd) < n_filled:
        x, y = (randint(1, grid_size), randint(1, grid_size))
        if (x, y) in out_corrd:
            pass
        else:
            out_corrd.append((x, y))
    return out_corrd
    
def get_distractors(ref_corrd, n_filled, grid_size):
    distractor = ref_corrd.copy()
    shuffle(distractor)
    distractor.pop()
    while len(distractor) < n_filled:
        x, y = (randint(1, grid_size), randint(1, grid_size))
        if (x, y) in ref_corrd:
            pass
        else:
            distractor.append((x, y))
    return distractor

# generate corrdinates of the correct answer
ans_corrd = get_coordinates(n_filled, grid_size)
distractors = []
while len(distractors) < len(ans_corrd):
    distractors.append(get_distractors(ans_corrd, n_filled, grid_size))
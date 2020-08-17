import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from itertools import islice
from tsp_class_fns import *

class Df():
    def __init__(self, raw_data_location):
        df = pd.read_csv(raw_data_location, header = 0)
        self.df = df

    from tsp_class_fns._tsp_df import tsp_df
    from tsp_class_fns._tsp_scan import tsp_scan
    from tsp_class_fns._tsp_struct import tsp_struct
    from tsp_class_fns._tsp_mrt import tsp_mrt
    from tsp_class_fns._tsp_switchrt import tsp_switchrt
    from tsp_class_fns._tsp_accuracy import tsp_accuracy
    from tsp_class_fns._tsp_stats import tsp_stats

import pandas as pd
import numpy as np
import os
from itertools import islice
from .HelperClasses import My_dict

def tsp_switchrt(self):
    df = self.df
    df1 = pd.DataFrame()
    df2 = pd.DataFrame()
    df3 = pd.DataFrame()

    for group_i, group_v in df.groupby(['type', 'occurence']):

        for index, row in group_v['response_time'].iteritems():
            if pd.notnull(row):
                continue
            else:
                group_v.at[index, 'response_time'] = np.NaN
        df1 = pd.concat([df1, group_v], sort=False)

    for gi, gv in df1.groupby(['type', 'occurence']):
        n = 0
        for index, row in gv.iterrows():
            n =  n + 1
        # ----- can change to % of trials ( m = x% of n) -----
        # here dicates over how many trials the RT is averaged over (m), dependant on how many 
        # trials are in the overall group (n).
        ##
        # eg, when the number of overall trials in the group is less than 3 (if n < 3), then 
        # the number of trials to average over is 0 (m = 0), and the rows are left empty (np.nan).
        if n < 3:
            m = 1
            for i, r in gv.iterrows():
                gv.at[i, 'first_switch_rt'] = np.NaN

        elif n >= 3 and n < 5:
            m = 1
        elif n >= 5:
            m = 1
    
        number_of_trials = 0
        overall_rt = 0
        # the 'islice' tells pandas to iterate with iterrows over the first 'm' rows
        for ind, ro in islice(gv.iterrows(), m):
            number_of_trials = number_of_trials + 1    
            overall_rt = overall_rt + ro['response_time']     
            j = (overall_rt/number_of_trials)
            gv.at[index, 'first_switch_rt'] = j
        df2 = pd.concat([df2, gv], sort=False)
    
    self.df = df2

    # when a group has less than 3 trials in it, the switch_rt is not calculated (m = 0). 
    # if there are NaN values in any of the rows of a column, that column returns NaN as a t-test 
    # value for any t-test calculations it is involved in. therefore i have excluded those rows below:
    for gri, grv in df2.groupby(['type', 'occurence']):
        for indx, rowx in grv['first_switch_rt'].iteritems():
            if pd.notnull(rowx):
                continue
            else:
                grv.drop(indx, inplace=True)
        df3 = pd.concat([df3, grv], sort=False)

    df4 = df3.set_index(['type', 'occurence'])

    first_switch_rt = My_dict()

    for indexx, roww in df4.iterrows():
        first_switch_rt.key = indexx
        first_switch_rt.value = roww['first_switch_rt']
        first_switch_rt.add(first_switch_rt.key, first_switch_rt.value)

    self.first_switch_rt = first_switch_rt
import pandas as pd
import numpy as np
import os
from .HelperClasses import My_dict

def tsp_accuracy(self):
    df = self.df
    df = df.set_index(['auto_participant_id', 'type', 'occurence'])

    #OVERALL % ACC
    number_correct = df['accuracy'].sum() 
    number_of_trials = df['participant_ans'].count()
    overall_accuracy = (number_correct / number_of_trials) * 100
    print('OVERALL ACCURACY =', overall_accuracy)

    ACC = My_dict()
    #GROUPED % ACC
    for group_i, group_v in df.groupby(level=[0,1,2]):
        for gi, gv in group_v.iterrows():
            overall_accuracy = 0
            corr = group_v['accuracy'].sum() 
            total = len(group_v['accuracy'])
            overall_accuracy = (corr / total) * 100
            a = np.array([overall_accuracy])

            for indexx, roww in group_v.iterrows():
                ACC.key = indexx
                ACC.value = a
                ACC.add(ACC.key, ACC.value)

        self.ACC = ACC
import pandas as pd
import numpy as np
import os

def tsp_df(self):
    df = self.df
    df1 = pd.DataFrame()
    for pid, g in df.groupby(['auto_participant_id']):
        g['index_raw'] = g.index
        n = 0
        for i, r in g.iterrows():
            n = n + 1
            g.at[i, 'index_raw'] = n
        df1 = pd.concat([df1, g], sort=False) 

    df1.rename(columns= {
        "trial_task_type":"type", 
        "answer_index":"target_ans",
        "response_answer":"participant_ans",
        "response_enabled_time":"time_response_enabled",
        "response_time":"time_response_submitted",    
        "stimulus_on":"time_start",
        "response_correct":"accuracy",
        }, inplace=True
        ) 

    # delete all columns but these
    df1 = df1[[
        'index_raw',
        'auto_participant_id',
        'participant_age',
        'participant_gender',
        'type',
        'trial_type',
        'trial_index',
        'time_elapsed',
        'time_start',
        'time_response_enabled',
        'time_response_submitted',
        'participant_ans',
        'target_ans',
        'accuracy'
    ]]

    self.df = df1
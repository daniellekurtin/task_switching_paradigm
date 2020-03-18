import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from pandas import DataFrame

def create_df(raw_data_location):
    df1 = pd.DataFrame()
    df2 = pd.DataFrame()
    df3 = pd.DataFrame(columns=[
    'participant_id',
    'block',
    'type', 
    'target_ans',
    'participant_ans',
    'time_start',
    'time_response_enabled',
    'time_response_submitted',
    'time_block',
    'response_time',
    'accuracy',
    'changed',
    'occurence'
    ])

    headers = [
    'participant_id',
    'type',
    'target_ans',
    'participant_ans',
    'time_start',
    'time_response_enabled',
    'time_response_submitted'
    ]

    df = pd.read_csv(raw_data_location, usecols = headers)

    df['time_block'] = df.time_start.diff()

    conditions = [
    df['target_ans'] == df['participant_ans']
    ]
    choices = [int(1)]


    df['response_time'] = np.where(
        df['time_response_submitted'] == int(-1), 3,
        df['time_response_submitted'].sub(df['time_response_enabled'], axis=0)
        )

    df['accuracy'] = np.select(conditions, choices, default=0)

    for group_index, group_value in df.groupby('participant_id'):
        x = 1
        for index, row in group_value.iterrows():
            if row['time_block'] > 100:
                x = x + 1
            else:
                x = x
            group_value.at[index,'block'] = x
        df1 = pd.concat([df1, group_value]) 
        df1.reset_index(drop = True, inplace = True)
    
    df1.set_index(['participant_id', 'block'], inplace = True)

    for group_index, group_value in df1.groupby(level=[0, 1]):
        group_value['changed'] = group_value['type'].ne(group_value['type'].shift(1).bfill()).astype(int)
        group_value.reset_index(drop = False, inplace = True)
        group_value.iloc[0, 11] = 1
        df2 = pd.concat([df2, group_value]) 
        df2.reset_index(drop = True, inplace = True)


    df2.set_index(['participant_id', 'block', 'type'], inplace = True)

    for group_index, group_value in df2.groupby(level=[0, 1]):
        group_value.reset_index(drop = False, inplace = True)
        array = np.zeros(shape = (100,3))
        for index, row in group_value.iterrows():
            if row['changed'] == 1:
                if row['type'] == "TrialDigitSpan":
                    array[index,0] =  1
                elif row['type'] == "TrialSpatialSpan":
                    array[index,1] =  1
                elif row['type'] == "TrialSpatialRotation":
                    array[index,2] =  1
            else:
                continue
            
        # sum_array tells you how many times each task type occured per block
        sum_array = array.sum(axis = 0)

        # determine occurence
        for group_i, group_v in group_value.groupby(['type']):
            j = 0
            for index, row in group_v.iterrows():
                if row['changed'] == 1:
                    j = j + 1
                else:
                    j = j
                group_v.at[index, 'occurence'] = j

            group_v.reset_index(drop = True, inplace = True)
            df3 = pd.concat([df3, group_v])
    
    df3.reset_index(drop = False, inplace = True)

    return df3
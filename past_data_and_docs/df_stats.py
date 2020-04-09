import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns 
import os 
from scipy import integrate 
from numpy import absolute, mean  
from pandas import DataFrame


df_behavstats2 = pd.DataFrame(columns = [
    'participant_id',
    'type',
    'block',
    'occurence',
    'MAD_rt',
    'median_rt',
    'mean_rt',
    'SD_rt',
])


# columns of interest from .csv file    
headers = [
    'participant_id',
    'block',
    'type',
    'target_ans',
    'participant_ans',
    'time_start',
    'time_response_enabled',
    'time_response_submitted',
    'response_time',
    'accuracy',
    'occurence'
]

# reading in .csv file
df = pd.read_csv(r'C:\Users\danie\Documents\SURREY\Project_1\task_switching_paradigm\data_v5_withoccurence.csv', usecols = headers)


# heirachical grouping of data
df.set_index(['participant_id', 'block', 'type', 'occurence'], inplace = True)
types = ['TrialDigitSpan', 'TrialSpatialSpan', 'TrialSpatialRotation']

# ---MRT---
df_mrt = df.drop(columns = [
    'time_start',
    'time_response_enabled',
    'time_response_submitted',
    'target_ans',
    'participant_ans',
    'accuracy'
])

# Calculate RT stats for each occurence per block, per type, per participant
for title, df_behavstats1 in df_mrt.groupby(level=[0, 1, 2, 3]):
    df_behavstats1 = df_behavstats1.apply(pd.to_numeric, errors = 'coerce').dropna(how = 'all')
    mask = df_behavstats1.index.get_level_values(3)
    mrt = df_behavstats1.mean()
    SD = (df_behavstats1.std())
    MAD = (mean(absolute(df_behavstats1 - mean(df_behavstats1))))
    med = (df_behavstats1.median())

    # I need to put the values above where they belong:
    # in the rows under their respective column, and next to their relevant indices.
    

    for row_index, row in df_behavstats1.iterrows():
        df_behavstats1.at[row_index,'MAD_rt']    = MAD
        df_behavstats1.at[row_index,'mean_rt']   = mrt
        df_behavstats1.at[row_index,'median_rt'] = med
        df_behavstats1.at[row_index, 'SD_rt']    = SD
    df_behavstats2 = pd.concat([df_behavstats2, df_behavstats1], sort=True) 
    df_behavstats2.reset_index(drop = True, inplace = True)

df_behavstats3 = df_behavstats2.drop(columns = [
    'type',
    'participant_id',
    'occurence',
    'block',
    'response_time'
])


df['MAD_rt']= df_behavstats3['MAD_rt']
df.MAD_rt = df.MAD_rt.astype(float)

df = df.drop(columns = [
    'time_start',
    'time_response_enabled',
    'time_response_submitted',
    'target_ans',
    'participant_ans',
])


# df_behavstats4 = pd.concat([df, df_behavstats3])
df.to_csv(r'data_v5_withoccurence_stats.csv')


    
        

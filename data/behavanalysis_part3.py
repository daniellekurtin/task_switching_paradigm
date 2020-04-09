import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns 
import os 
from scipy import integrate, stats
from numpy import absolute, mean  
from pandas import DataFrame
from os import getcwd, path, makedirs

#####################################################################################################
# Organize, open, and read raw data


df_behavstats2 = pd.DataFrame(columns = [
    'participant_id',
    'type',
    'block',
    'occurence',
    'MAD_rt',
    'median_rt',
    'mean_rt',
    'SD_rt',
    'switchtrial_rt1',
    'switchtrial_rt2',
    # 'switchtrial_rt3',
    'switchtrial_rt123'
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

# reading in .csv file printed from xxbn
df = pd.read_csv(r'C:\Users\danie\Documents\SURREY\Project_1\task_switching_paradigm\pilot3_withoccurence.csv', usecols = headers)


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

#####################################################################################################
# Determine the descriptive statistics for the behavioral pilot, and output to a .csv

# Calculate RT for each block, per type- print and plug into the table 
for title, df_behavstats1 in df_mrt.groupby(level=[1, 2]):
    df_behavstats1 = df_behavstats1.apply(pd.to_numeric, errors = 'coerce').dropna(how = 'all')
    mask = df_behavstats1.index.get_level_values(3)
    mrt = df_behavstats1.mean()
    med = df_behavstats1.median()
    SD = (df_behavstats1.std())
    MAD = (mean(absolute(df_behavstats1 - mean(df_behavstats1))))


# Calculate RT stats for each occurence per block, per type, per participant
for title, df_behavstats1 in df_mrt.groupby(level=[0, 1, 2, 3]):
    df_behavstats1 = df_behavstats1.apply(pd.to_numeric, errors = 'coerce').dropna(how = 'all')
    mask = df_behavstats1.index.get_level_values(3)
    mrt = df_behavstats1.mean()
    SD = (df_behavstats1.std())
    MAD = (mean(absolute(df_behavstats1 - mean(df_behavstats1))))
    med = (df_behavstats1.median())
    switchtrial1 = df_behavstats1['response_time'].iloc[0]
    switchtrial2 = df_behavstats1['response_time'].iloc[1]
    # switchtrial3 = df_behavstats1['response_time'].iloc[2]
    switchtrial12 = ((switchtrial1 + switchtrial2) / 2)
    # switchtrial123 = ((switchtrial1 + switchtrial2 + switchtrial3) / 3)

    for row_index, row in df_behavstats1.iterrows():
        df_behavstats1.at[row_index,'MAD_rt']    = MAD
        df_behavstats1.at[row_index,'mean_rt']   = mrt
        df_behavstats1.at[row_index,'median_rt'] = med
        df_behavstats1.at[row_index, 'SD_rt']    = SD
        df_behavstats1.at[row_index, 'switchtrial_rt1'] = switchtrial1
        df_behavstats1.at[row_index, 'switchtrial_rt2'] = switchtrial2
        # df_behavstats1.at[row_index, 'switchtrial_rt3'] = switchtrial3
        df_behavstats1.at[row_index, 'switchtrial_rt123'] = switchtrial12
    df_behavstats2 = pd.concat([df_behavstats2, df_behavstats1], sort=True) 


# this information is largely contained in the first columns, the indices it is grouped by
df_behavstats3 = df_behavstats2.drop(columns = [
    'type',
    'participant_id',
    'occurence',
    'block',
    'response_time'
])

# this gets rid of duplicate rows
df_behavstats3.drop_duplicates(subset ="MAD_rt", keep = "first", inplace = True) 

df_behavstats3.to_csv(r'pilot3_RT_stats.csv')

#####################################################################################################
# Define data variables

mean   = df_behavstats3['mean_rt'] 
median = df_behavstats3['median_rt'] 
rt1    = df_behavstats3['switchtrial_rt1']
rt2    = df_behavstats3['switchtrial_rt2']
# rt3    = df_behavstats3['switchtrial_rt3']
rt123  = df_behavstats3['switchtrial_rt123']
MAD    = df_behavstats3['MAD_rt']
SD     = df_behavstats3['SD_rt'] 


#####################################################################################################
# TTests- Standard and Welch's (in that order)

a = stats.ttest_ind(mean, rt1)
b = stats.ttest_ind(mean, rt2)
# c = stats.ttest_ind(mean, rt3)
MEANvsAVRT = stats.ttest_ind(mean, rt123)

d = stats.ttest_ind(median, rt1)
e = stats.ttest_ind(median, rt2)
# f = stats.ttest_ind(median, rt3)
MEDvsAVRT = stats.ttest_ind(median, rt123) 

a1 = stats.ttest_ind(mean, rt1, equal_var = False)
b1 = stats.ttest_ind(mean, rt2, equal_var = False)
# c1 = stats.ttest_ind(mean, rt3, equal_var = False)
MEANvsAVRT1 = stats.ttest_ind(mean, rt123, equal_var = False)

d1 = stats.ttest_ind(median, rt1, equal_var = False)
e1 = stats.ttest_ind(median, rt2, equal_var = False)
# f1 = stats.ttest_ind(median, rt3, equal_var = False)
MEDvsAVRT1 = stats.ttest_ind(median, rt123, equal_var = False) 

#####################################################################################################
# Print and Save that Shit

# print('STANDARD TTESTS')
# print(a,b,d,e,f)

# print('WELCH'S TTESTS')
# print(a1,b1,c1,d1,e1,f1,)

file_path = (r"C:\Users\danie\Documents\SURREY\Project_1\task_switching_paradigm\data\public\MRT\Stats")
file_title = ("pilot3_RT_stats")
file_name = path.join(file_path, file_title + ".txt")

w = open(file_name, 'w+')
w.write(str(a))

#####################################################################################################
# When in doubt, boxplot it out

# data = [mean, median, rt1, rt2, rt123]
# fig1, ax1 = plt.subplots()
# ax1.set_title('Reaction Times for Task Switching Paradigm Pilot 2')
# ax1.boxplot(data)
# plt.xticks([1, 2, 3, 4, 5, 6], ['mean', 'median', 'rt1', 'rt2', 'rt123'])
# plt.show()




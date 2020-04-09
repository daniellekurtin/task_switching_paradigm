import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns 
import os 
from scipy import integrate, stats
from numpy import absolute, mean  
from pandas import DataFrame
from itertools import islice
import researchpy as rp
import seaborn as sns
import statsmodels.api as sm
from statsmodels.formula.api import ols
import statsmodels.stats.multicomp


#####################################################################################################
# Before beginning: make sure the file name matches the version of experiment you want to analyze.
# Ensure the output .csv's reflect the desired version as well. 


# #####################################################################################################
# # Organize, open, and read raw data

# df_accuracy = pd.DataFrame(columns=[
#     'participant_id',
#     'type',
#     'block',
#     'occurence',
#     'accuracy',
#     'index1',
#     'cumu_acc',
#     'percent_acc'
# ])

# df_accuracy1 = pd.DataFrame(columns=[
#     'participant_id',
#     'type',
#     'block',
#     'occurence',
#     'accuracy',
#     'index1',
#     'cumu_acc',
#     'percent_acc'
# ])

# df_accuracy2 = pd.DataFrame(columns=[
#     'participant_id',
#     'type',
#     'block',
#     'occurence',
#     'accuracy',
#     'index1',
#     'cumu_acc',
#     'percent_acc'
# ])


# # columns of interest from .csv file    
# headers = [
#     'participant_id',
#     'block',
#     'type',
#     'target_ans',
#     'participant_ans',
#     'accuracy',
#     'occurence'
# ]

# # reading in .csv file printed behavanalysis_part1
# df = pd.read_csv(r'C:\Users\danie\Documents\SURREY\Project_1\task_switching_paradigm\pilot3_withoccurence.csv', usecols = headers)


# # heirachical grouping of data
# df.set_index(['participant_id', 'block', 'type', 'occurence'], inplace = True)
# types = ['TrialDigitSpan', 'TrialSpatialSpan', 'TrialSpatialRotation']


# #####################################################################################################
# #---ACCURACY---

# df_acc = df.drop(columns = [
#     'target_ans',
#     'participant_ans'
# ])

# # calc. cumulative accuracy for each block, per type, per participant
# for title, df_acc1 in df_acc.groupby(level=[0, 1, 2, 3]): 
#     df_acc1.reset_index(drop = False, inplace = True)
#     y = 0
#     for row_index, row in df_acc1.iterrows():
#         if row['accuracy'] == 1:
#             y = y + 1
#         else:
#             y = y + 0
#         df_acc1.at[row_index,'cumu_acc'] = y
#         df_acc1.at[row_index,'index1'] = row_index
#         #print(row_index, row.values)
#     df_accuracy = pd.concat([df_accuracy, df_acc1], sort = False) 
#     df_accuracy.reset_index(drop = True, inplace = True)


# # df_accuracy.to_csv(r'pilot3_ACC_stats.csv')

# ###############################################################################################
# # Determine the descriptive statistics for the behavioral pilot, and output to a .csv
# # 1. Determine percent accuracy grouped by all indices
# # 2. Determine percent accuracy for the first three trials groups by all indices
# # 3. TTest to compare the two

# ##############################################################################################
# # This function determines percent accuracy for all participants, per block, per type

# df_accuracy.set_index(['participant_id', 'type', 'block', 'occurence'], inplace = True)
# types = ['TrialDigitSpan', 'TrialSpatialSpan', 'TrialSpatialRotation']

# for group_j, group_w in df_accuracy.groupby(level=[1, 2]):

#     number_of_trials = 0
#     overall_accuracy = 0

#     for index, row in group_w.iterrows():

#         number_of_trials = number_of_trials + 1    
#         overall_accuracy = overall_accuracy + row['accuracy']     
#         k = ((overall_accuracy/number_of_trials) * 100)
#         group_w.at[index, 'percent_acc'] = k

#     group_w.reset_index(drop = False, inplace = True)
#     df_accuracy2 = pd.concat([df_accuracy2, group_w], sort=False)
    
# df_accuracy2.to_csv('pilot3_ACC_stats_group.csv')


# ##############################################################################################
# # This function determines percent accuracy per person, per block, per type, per occurence

# df_accuracy.reset_index(drop=False, inplace=True)
# df_accuracy.set_index(['participant_id', 'type', 'block', 'occurence'], inplace = True)
# types = ['TrialDigitSpan', 'TrialSpatialSpan', 'TrialSpatialRotation']

# df_accuracy.groupby(level=[0, 1, 2, 3])

# for group_i, group_v in df_accuracy.groupby(level=[0, 1, 2, 3]):

#     number_of_trials = 0
#     overall_accuracy = 0

#     for index, row in group_v.iterrows():

#         number_of_trials = number_of_trials + 1    
#         overall_accuracy = overall_accuracy + row['accuracy']     
#         j = ((overall_accuracy/number_of_trials) * 100)
#         group_v.at[index, 'percent_acc'] = j
    
#     group_v.drop_duplicates(subset ='percent_acc', keep = "first", inplace = True)
#     group_v.reset_index(drop = False, inplace = True)
#     df_accuracy1 = pd.concat([df_accuracy1, group_v])

# df_accuracy1.to_csv('pilot3_ACC_stats_individual.csv')



headers = [
    'participant_id',
    'block',
    'type',
    'occurence',
    'accuracy',
] 

df_accuracy = pd.read_csv(r'C:\Users\danie\Documents\SURREY\Project_1\task_switching_paradigm\pilot3_withoccurence.csv', usecols = headers)
df_accuracy1 = pd.DataFrame()
df_accuracy2 = pd.DataFrame()


# OVERALL % ACCURACY

df_accuracy.set_index(['participant_id', 'type', 'block', 'occurence'], inplace = True)

for group_i, group_v in df_accuracy.groupby(level=[0, 1, 2, 3]):

    number_of_trials = 0
    overall_accuracy = 0

    for index, row in group_v.iterrows():

        number_of_trials = number_of_trials + 1    
        overall_accuracy = overall_accuracy + row['accuracy']     
        j = ((overall_accuracy/number_of_trials) * 100)
        group_v.at[index, 'overall_percent_acc'] = j

    group_v.reset_index(drop = False, inplace = True)
    df_accuracy1 = pd.concat([df_accuracy1, group_v])

df_accuracy1.reset_index(drop = True, inplace = True)


# SWITCH % ACCURACY

df_accuracy1.set_index(['participant_id', 'type', 'block', 'occurence'], inplace = True)

for group_i, group_v in df_accuracy1.groupby(level=[0, 1, 2, 3]):
    n = 0

    for index, row in group_v.iterrows():
        n =  n + 1
    
    if n < 3:
        m = 0
        for index, row in group_v.iterrows():
            group_v.at[index, 'switch_percent_acc'] = np.nan
    
    elif n >= 3 and n < 5:
        m = 2

    elif n >= 5:
        m = 4

    number_of_trials = 0
    overall_accuracy = 0

    for index, row in islice(group_v.iterrows(), m):

        number_of_trials = number_of_trials + 1    
        overall_accuracy = overall_accuracy + row['accuracy']     
        j = ((overall_accuracy/number_of_trials) * 100)
        group_v.at[index, 'switch_percent_acc'] = j

    group_v.reset_index(drop = False, inplace = True)
    df_accuracy2 = pd.concat([df_accuracy2, group_v])
 
df_accuracy2.to_csv('pilot3_ACC_stats.csv')

df_accuracy2.set_index(['participant_id', 'type', 'block', 'occurence'], inplace = True)
df_accuracy2.groupby(level=[0,1,2,3])
df_accuracy2.drop_duplicates(subset ='switch_percent_acc', keep = "first", inplace = True)
df_accuracy2.to_csv('oyvey.csv')

############################################################################################
# ANOVA

model = ols('df_accuracy2["overall_percent_acc"] ~ C(df_accuracy2["block"])*C(df_accuracy2["type"])*C(df_accuracy2["participant_id"])', df_accuracy2).fit()

print(f"Overall model F({model.df_model: .0f},{model.df_resid: .0f}) = {model.fvalue: .3f}, p = {model.f_pvalue: .4f}")

model.summary()

res = sm.stats.anova_lm(model, typ= 2)
print(res)
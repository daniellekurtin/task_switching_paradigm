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

headers = [
    'participant_id',
    'block',
    'type',
    'occurence',
    'switch_type',
    'accuracy',
] 

df_accuracy = pd.read_csv(r'C:\Users\danie\Documents\SURREY\Project_1\task_switching_paradigm\pilot4_withoccurence.csv', usecols = headers)
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

x = 0

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

    x = x + 1

    for index, row in islice(group_v.iterrows(), m):

        number_of_trials = number_of_trials + 1    
        overall_accuracy = overall_accuracy + row['accuracy']     
        j = ((overall_accuracy/number_of_trials) * 100)
        group_v.at[index, 'switch_percent_acc'] = j        
        group_v.at[index, 'drop_column'] = x

    group_v.reset_index(drop = False, inplace = True)
    df_accuracy2 = pd.concat([df_accuracy2, group_v], sort=True)
 

df_accuracy2.drop_duplicates(subset ='drop_column', keep = "first", inplace = True)
df_accuracy2.drop(columns=['accuracy', 'drop_column'], inplace=True)
df_accuracy2.to_csv('pilot4_ACC_stats.csv')


############################################################################################
# ANOVA

df_accuracy2.columns = [
    'block', 
    'occurence', 
    'overall_percent_acc',
    'participant_id',
    'switch_percent_acc',
    'type',
    'switch_type'
    ]

model1 = ols(
    'overall_percent_acc ~ C(block) + C(type) + C(participant_id) + C(switch_type) + C(block):C(switch_type) + C(type):C(switch_type) + C(participant_id):C(switch_type) + C(block):C(type) + C(block):C(participant_id) + C(type):C(participant_id)',
    data=df_accuracy2
    ).fit()

anova_table1 = sm.stats.anova_lm(model1, typ=2)
print(anova_table1)
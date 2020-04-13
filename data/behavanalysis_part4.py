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
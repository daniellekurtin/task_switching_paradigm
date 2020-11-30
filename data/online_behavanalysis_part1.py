import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns 
import os 
from scipy import integrate 
from numpy import absolute, mean  
from pandas import DataFrame
from online_behavanalysis_part2 import create_df2
from online_behavanalysis_part3 import create_df3
from online_behavanalysis_part4 import create_df4

# Make the Occurence Column 
raw_data_location2 = open(r'C:\Users\danie\Documents\SURREY\Project_1\TaskSwitchingParadigm\online_TSP\second_online_cohort\data_clean.csv')
df = create_df2(raw_data_location2)
path = (r'C:\Users\danie\Documents\SURREY\Project_1\TaskSwitchingParadigm\online_TSP\second_online_cohort')


df.drop(columns=[
    'blueprint_id',
    'view_history',
    'internal_node_id',
    'check_times',
    'responses',
])


#-----DATA-----
#-calculating blocks-

# creating new df columns
df['time_block'] = df.time_start.diff()

# defining RT
df['response_time'] = np.where(
    df['time_response_submitted'] == int(-1),
    3,
    df['time_response_submitted'].sub(df['time_response_enabled'], axis=0)
)


#-----ANALYSIS-----

# heirachical grouping of data
df.set_index(['auto_participant_id', 'type' ], inplace = True)

# ---MRT---
df_mrt = df.drop(columns = [
    'time_start',
    'time_response_enabled',
    'time_response_submitted',
    'time_block',
    'rt',	
    'responses'
])

# mean response time (mrt) calc. for each block, per type, per participant
for title, df_mrt1 in df_mrt.groupby(level=[0, 1]):
    df_mrt1 = df_mrt1.apply(pd.to_numeric, errors = 'coerce').dropna(how = 'all')
    mask = df_mrt1.index.get_level_values(1)
    mrt = df_mrt1.groupby(level=[0, 1]).mean()
    # print(mrt)
    # print('\nPLOTTING MRT (participant_id, type) = {}'.format(title))

print('\n********************************************************************************************************************************************')

df_mrt.reset_index(drop=False, inplace=False)

name='pilot2_WithOccurence.csv'
dest = os.path.join(path, name)
df_mrt.to_csv(dest)

raw_data_location3 = open(r'C:\Users\danie\Documents\SURREY\Project_1\TaskSwitchingParadigm\online_TSP\second_online_cohort\pilot2_WithOccurence.csv')           
df3 = create_df3(raw_data_location3)
name='pilot2_WithSwitchCosts.csv'
dest = os.path.join(path, name)
df3.to_csv(dest)


raw_data_location4 = open(r'C:\Users\danie\Documents\SURREY\Project_1\TaskSwitchingParadigm\online_TSP\second_online_cohort\pilot2_WithSwitchCosts.csv')   
df4 = create_df4(raw_data_location4)
name='pilot2_WithAccuracy.csv'
dest = os.path.join(path, name)
df4.to_csv(dest)
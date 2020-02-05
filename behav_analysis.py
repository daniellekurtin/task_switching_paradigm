import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

###
###
###
###
###
# columns of interest from .csv file
headers = ['participant_id', 'type', 'target_ans', 'participant_ans', 'time_start', 'time_response_enabled', 'time_response_submitted']
# reading in .csv file
df = pd.read_csv(r'C:\Users\danie\Documents\SURREY\Project_1\oxbridge_brainhack_2019\data\public\ExperimentTaskSwitch-v0.0.2_trials-v0.0.1.csv', usecols = headers)
###
###
###
###
###

# creating an empty df with column names only for data analysis later on
df_new = pd.DataFrame(columns=['participant_id', 'type', 'target_ans', 'participant_ans', 'time_start', 'time_response_enabled', 'time_response_submitted', 'time_block', 'response_time', 'accuracy', 'block'])
df_accuracy = pd.DataFrame(columns=['participant_id', 'type', 'block', 'accuracy', 'cumu_acc'])

#-----DATA-----
#-calculating blocks-

# creating new df columns
df['time_block'] = df.time_start.diff()

# defining RT and A
df['response_time'] = np.where(df['time_response_submitted'] == int(-1), 3, df['time_response_submitted'].sub(df['time_response_enabled'], axis = 0)) 

conditions = [
    df['target_ans'] == df['participant_ans']
    ]
choices = [int(1)]
df['accuracy'] = np.select(conditions, choices, default = 0)

# grouping by participant_id
pid_group = df.groupby('participant_id')

# block determination for each participant (new block starts when time interval between the start of questions > 100s)
for group_name, df_group in pid_group:
    print('\nCREATING TABLE {}('.format(group_name))
    x = 1
    for row_index, row in df_group.iterrows():
        if row['time_block'] > 100:
            x = x + 1
        else:
            x = x
        df_group.at[row_index,'block'] = x
    df_new = pd.concat([df_new, df_group]) 
    df_new.reset_index(drop = True, inplace = True)
print('\n********************************************************************************************************************************************')

# # *****troubleshoot
# print(df_new)
# # *****

# exporting data to .csv file 
df_new.to_csv(r'data1')



#-----ANALYSIS-----

# heirachical grouping of data
df_new.set_index(['participant_id', 'type', 'block'], inplace = True)
types = ['TrialDigitSpan', 'TrialSpatialSpan', 'TrialSpatialRotation']

#---MRT---
df_mrt = df_new.drop(columns = ['time_start', 'time_response_enabled', 'time_response_submitted', 'time_block', 'target_ans', 'participant_ans', 'accuracy'])

# mean response time (mrt) calc. for each block, per type, per participant
for title, df_mrt1 in df_mrt.groupby(level=[0, 1]):
    df_mrt1 = df_mrt1.apply(pd.to_numeric, errors = 'coerce').dropna(how = 'all')
    mask = df_mrt1.index.get_level_values(2)
    mrt = df_mrt1.groupby(level=2).mean()
    #*****troubleshoot
    #print(mrt)
    #*****
    print('\nPLOTTING MRT (participant_id, type) = {}('.format(title))
    mrt.plot(legend = True).get_figure().savefig('MRT/MRT: {}'.format(title))
print('\n********************************************************************************************************************************************')

#---ACCURACY---

df_acc = df_new.drop(columns = ['time_start', 'time_response_enabled', 'time_response_submitted', 'time_block', 'target_ans', 'participant_ans', 'response_time'])

# calc. cumulative accuracy for each block, per type, per participant
for title, df_acc1 in df_acc.groupby(level=[0, 1, 2]): 
    df_acc1.reset_index(drop = False, inplace = True)
    y = 0
    for row_index, row in df_acc1.iterrows():
        if row['accuracy'] == 1:
            y = y + 1
        else:
            y = y + 0
        df_acc1.at[row_index,'cumu_acc'] = y
    df_accuracy = pd.concat([df_accuracy, df_acc1]) 
    df_accuracy.reset_index(drop = True, inplace = True)
    #*****troubelshoot
    #print(df_acc1)
    #*****
    print('\nCUMULATIVE ACCURACY FOR (participant_id, type, block) = {}('.format(title))
print('\n********************************************************************************************************************************************')

df_accuracy.set_index(['participant_id', 'type', 'block'], inplace = True)
df_accuracy1 = df_accuracy.drop(columns = ['accuracy'])

for title, df_accuracy2 in df_accuracy1.groupby(level=[0, 1]):
    df_accuracy2 = df_accuracy2.apply(pd.to_numeric, errors = 'coerce').dropna(how = 'all')
    mask = df_accuracy2.index.get_level_values(2)
    acc = df_accuracy2.groupby(level=2)
    #*****troubleshoot
    #print(acc)
    #*****
    acc.plot(legend = True)
    plt.show()
    #plt.savefig('accuracy/ACC: {}'.format(title))
    print('\nPLOTTING ACCURACY (participant_id, type) = {}('.format(title))
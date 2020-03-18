import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns 
import os 
from scipy import integrate 
from numpy import absolute, mean  
from pandas import DataFrame
from xxbn import create_df

# columns of interest from .csv file
headers = [
    'participant_id',
    'type',
    'target_ans',
    'participant_ans',
    'time_start',
    'time_response_enabled',
    'time_response_submitted'
]
# reading in .csv file
df = pd.read_csv(r'C:\Users\danie\Documents\SURREY\Project_1\task_switching_paradigm\data\public\ExperimentTaskSwitch-v0.0.3_trials-v0.0.1.csv', usecols = headers)

# creating an empty df with column names only for data analysis later on
df_new = pd.DataFrame(columns=[
    'participant_id',
    'type', 
    'target_ans',
    'participant_ans',
    'time_start',
    'time_response_enabled',
    'time_response_submitted',
    'time_block',
    'response_time',
    'accuracy',
    'block'
])

df_accuracy = pd.DataFrame(columns=[
    'participant_id',
    'type',
    'block',
    'accuracy',
    'index1',
    'cumu_acc'
])

#-----DATA-----
#-calculating blocks-

# creating new df columns
df['time_block'] = df.time_start.diff()

# defining RT and A
df['response_time'] = np.where(
    df['time_response_submitted'] == int(-1),
    3,
    df['time_response_submitted'].sub(df['time_response_enabled'], axis=0)
)

conditions = [
    df['target_ans'] == df['participant_ans']
    ]
choices = [int(1)]
df['accuracy'] = np.select(conditions, choices, default=0)

# grouping by participant_id
pid_group = df.groupby('participant_id')

# block determination for each participant 
# (new block starts when time interval between the start of questions > 100s)
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

# exporting data to .csv file 
df_new.to_csv(r'data_v5.csv')

 
#-----ANALYSIS-----

# heirachical grouping of data
df_new.set_index(['participant_id', 'block', 'type'], inplace = True)
types = ['TrialDigitSpan', 'TrialSpatialSpan', 'TrialSpatialRotation']

# ---MRT---
df_mrt = df_new.drop(columns = [
    'time_start',
    'time_response_enabled',
    'time_response_submitted',
    'time_block',
    'target_ans',
    'participant_ans',
    'accuracy'
])

# mean response time (mrt) calc. for each block, per type, per participant
for title, df_mrt1 in df_mrt.groupby(level=[0, 1, 2]):
    df_mrt1 = df_mrt1.apply(pd.to_numeric, errors = 'coerce').dropna(how = 'all')
    mask = df_mrt1.index.get_level_values(2)
    mrt = df_mrt1.mean()
    #print('\nPLOTTING MRT (participant_id, type) = {}'.format(title))

    for i in mrt:
        plt.title('Mean Reaction Time for {}'.format(title))
        plt.plot(mrt)
        plt.xlabel('Block')
        plt.ylabel('Mean Reaction Time (sec)')
        plt.axis([1, 4, 0, 3.0])
        path = (r'C:\Users\danie\Documents\SURREY\Project_1\task_switching_paradigm\data\public\MRT')
        # plt.annotate(MRT_data, xy =(3,0.5))
        figname = 'fig_{}.png'.format(title)
        dest = os.path.join(path, figname)
        plt.savefig(dest)  
        plt.cla()
    print('\nYOU GOT THIS GURL SMASH THE ANALYSIS')


#---ACCURACY---

df_acc = df_new.drop(columns = [
    'time_start',
    'time_response_enabled',
    'time_response_submitted',
    'time_block',
    'target_ans',
    'participant_ans',
    'response_time'
])

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
        df_acc1.at[row_index,'index1'] = row_index
        #print(row_index, row.values)
    df_accuracy = pd.concat([df_accuracy, df_acc1], sort = False) 
    df_accuracy.reset_index(drop = True, inplace = True)

    # print('\nCUMULATIVE ACCURACY FOR (participant_id, type, block) = {}'.format(title))

df_accuracy.set_index(['participant_id', 'type', 'block'], inplace = True)
df_accuracy = df_accuracy.drop(columns = ['accuracy']) 

# integral for cumulative accuracy
acc_integral = np.array([])
for title, df_integrate in df_accuracy.groupby(level=[0, 1, 2]): 
    integral_y = df_integrate['cumu_acc'].values
    integral_x = df_integrate['index1'].values
    integral = integrate.cumtrapz(integral_y, integral_x, initial = 0)

    acc_integral = np.concatenate([acc_integral, integral])

    # print('\nRATE OF ACCURACY FOR (participant_id, type, block) = {}'.format(title))

df_accuracy['acc_integral'] = acc_integral

# differential for cumulative accuracy
acc_differential = np.array([])
for title, df_differentiate in df_accuracy.groupby(level=[0, 1, 2]): 
    differential_y = df_differentiate['acc_integral'].values
    differential_x = df_differentiate['index1'].values
    if len(differential_x) < 2:
        differential = [0]
    else:
        differential = np.gradient(differential_y)

    acc_differential = np.concatenate([acc_differential, differential])

    # print('\nSTABILISATION OF ACCURACY FOR (participant_id, type, block) = {}'.format(title))
print('\n********************************************************************************************************************************************')

df_accuracy['acc_differential'] = acc_differential

df_accuracy_cumulative = df_accuracy.drop(columns = ['index1', 'acc_integral', 'acc_differential'])
df_accuracy_cumulative.name = 'dfc'
df_accuracy_integral = df_accuracy.drop(columns = ['index1', 'cumu_acc', 'acc_differential'])
df_accuracy_integral.name = 'dfi' 
df_accuracy_differential = df_accuracy.drop(columns = ['index1', 'cumu_acc', 'acc_integral']) 
df_accuracy_differential.name = 'dfd' 

accuracy_plots = [df_accuracy_cumulative, df_accuracy_integral, df_accuracy_differential]

fig, ax = plt.subplots()
line_labels = ["Block 1", "Block 2", "Block 3", "Block 4"]

# plot cumulative, integral, differential accuracy
for i in accuracy_plots:
    for title, df_accuracy1 in i.groupby(level=[0, 1]):
        df_accuracy1 = df_accuracy1.apply(pd.to_numeric, errors = 'coerce').dropna(how = 'all')
        mask = df_accuracy1.index.get_level_values(2)
        acc = df_accuracy1.groupby(level=2)
        ACC_data = df_accuracy_cumulative

        if i.name == 'dfc':
            # print('\nPLOTTING CUMULATIVE ACCURACY (participant_id, type) = {}('.format(title))
            acc.plot(ax = ax)
            plt.title('Cumulative Accuracy for {}'.format(title))
            plt.legend(labels = line_labels, loc = "upper left", title = "Block #")    
            plt.xlabel('Trial')
            plt.ylabel('Cumulative Accuracy')
            plt.xlim([0, 30.0])
            plt.ylim(0, 30.0)
            plt.tick_params(
                axis = 'x', 
                which = 'both',  
                bottom = False,
                top = False,
                labelbottom = False
                )
            path = (r'C:\Users\danie\Documents\SURREY\Project_1\task_switching_paradigm\data\public\accuracy\cumulative')
            figname = 'fig_{}.png'.format(title)
            dest = os.path.join(path, figname)
            plt.savefig(dest)  
            plt.cla()

        if i.name == 'dfi':
            # print('\nPLOTTING RATE OF ACCURACY (participant_id, type) = {}('.format(title))
            acc.plot(ax = ax)

            plt.title('Integrated Rate of Accuracy for {}'.format(title))
            plt.legend(labels = line_labels, loc = "upper left", title = "Block #")   
            plt.xlabel('Trial')
            plt.ylabel('Rate of Accuracy')
            plt.xlim([0, 30.0])
            plt.ylim(0, 400.0)
            plt.tick_params(
                axis = 'x', 
                which = 'both',  
                bottom = False,
                top = False,
                labelbottom = False
                )
            path = (r'C:\Users\danie\Documents\SURREY\Project_1\task_switching_paradigm\data\public\accuracy\integral')
            figname = 'fig_{}.png'.format(title)
            dest = os.path.join(path, figname)
            plt.savefig(dest)  
            plt.cla()
        
        if i.name == 'dfd':
            # print('\nPLOTTING STABILISATION OF ACCURACY (participant_id, type) = {}('.format(title))
            acc.plot(ax = ax)

            plt.title('Stabilisation Rate of Accuracy for {}'.format(title))
            plt.legend(labels = line_labels, loc = "upper left", title = "Block #")   
            plt.xlabel('Trial')
            plt.ylabel('Stabilisation of Accuracy')
            plt.xlim([0, 30.0])
            plt.ylim(0, 30.0)
            plt.tick_params(
                axis = 'x', 
                which = 'both',  
                bottom = False,
                top = False,
                labelbottom = False
                )
            path = (r'C:\Users\danie\Documents\SURREY\Project_1\task_switching_paradigm\data\public\accuracy\differential')
            # plt.annotate(ACC_data, xy =(10,25))
            figname = 'fig_{}.png'.format(title)
            dest = os.path.join(path, figname)
            plt.savefig(dest)  
            plt.cla()

# Make the Occurence Column 
raw_data_location = open(r'C:\Users\danie\Documents\SURREY\Project_1\task_switching_paradigm\data\public\ExperimentTaskSwitch-v0.0.3_trials-v0.0.1.csv')
df = create_df(raw_data_location)
df.to_csv(r'data_v5_withoccurence.csv')
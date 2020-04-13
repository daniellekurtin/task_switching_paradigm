import pandas as pd
import numpy as np
from scipy import integrate, stats
from numpy import absolute, mean  
from itertools import islice

headers = [
    'participant_id',
    'type',
    'block',
    'occurence',
    'response_time',
    'accuracy'
]

df = pd.read_csv(r'C:\Users\danie\Documents\SURREY\Project_1\task_switching_paradigm\pilot3_withoccurence.csv', usecols = headers)

df_behavstats1 = pd.DataFrame()
df_behavstats = pd.DataFrame()


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# LOOP WHICH CALCULATES AND CONCATS MAD, SD, MRT, MED
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

df.set_index(['participant_id', 'block', 'type', 'occurence'], inplace = True)
df_rt = df.drop(columns = [
    'accuracy'
])

for group_i, group_v in df_rt.groupby(level=[0, 1, 2, 3]):
    group_v = group_v.apply(pd.to_numeric, errors = 'coerce').dropna(how = 'all')
    mask = group_v.index.get_level_values(3)

    n = 0
    for index, row in group_v.iterrows():
        n =  n + 1

    mrt = group_v.mean()
    SD = group_v.std()
    MAD = mean(absolute(group_v - mean(group_v)))
    med = group_v.median()
    switchtrial0 = group_v['response_time'].iloc[0]
    switchtrial1 = group_v['response_time'].iloc[1]
    if n > 2:
        switchtrial2 = group_v['response_time'].iloc[2]

    for index, row in group_v.iterrows():
        group_v.at[index, 'mean_rt'] = mrt
        group_v.at[index, 'SD_rt'] = SD
        group_v.at[index, 'MAD_rt'] = MAD
        group_v.at[index, 'median_rt'] = med
        group_v.at[index, 'rt_trial_1'] = switchtrial0
        group_v.at[index, 'rt_trial_2'] = switchtrial1
        if n < 3:
            group_v.at[index, 'rt_trial_3'] = np.nan
        else:
            group_v.at[index, 'rt_trial_3'] = switchtrial2

    group_v.reset_index(drop = False, inplace = True)
    df_behavstats1 = pd.concat([df_behavstats1, group_v], sort=False) 


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# LOOP WHICH CALCULATES AND CONCATS SWITCH RT
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

df_behavstats1.set_index(['participant_id', 'block', 'type', 'occurence'], inplace = True)

for group_i, group_v in df_behavstats1.groupby(level=[0, 1, 2, 3]):

    n = 0
    for index, row in group_v.iterrows():
        n =  n + 1
    
    # here dicates over how many trials the RT is averaged over (m), dependant on how many 
    # trials are in the overall group (n).
    ##
    # eg, when the number of overall trials in the group is less than 3 (if n < 3), then 
    # the number of trials to average over is 0 (m = 0), and the rows are left empty (np.nan).
    if n < 3:
        m = 0
        for index, row in group_v.iterrows():
            group_v.at[index, 'switch_rt'] = np.nan
    elif n >= 3 and n < 5:
        m = 2
    elif n >= 5:
        m = 3

    number_of_trials = 0
    overall_rt = 0
    # the 'islice' tells pandas to iterate with iterrows over the first 'm' rows, where 'm' is 
    # dictated above and depends on the overall number of trials, 'n', in the group.
    for index, row in islice(group_v.iterrows(), m):
        number_of_trials = number_of_trials + 1    
        overall_rt = overall_rt + row['response_time']     
        j = (overall_rt/number_of_trials)
        group_v.at[index, 'switch_rt'] = j
    
    group_v.reset_index(drop = True, inplace = False)
    df_behavstats = pd.concat([df_behavstats, group_v], sort=True)

df_behavstats = df_behavstats.drop(columns=['response_time'])
df_behavstats.drop_duplicates(subset="MAD_rt", keep='first', inplace=True)

# when a group has less than 3 trials in it, the switch_rt is not calculated (m = 0). 
# if there are NaN values in any of the rows of a column, that column returns NaN as a t-test 
# value for any t-test calculations it is involved in. therefore i have excluded those rows below:
print("")
print("")
print('HI DANIELLE!!!! BELOW DISPLAYS THE GROUP(S) WHICH HAVE BEEN EXCLUDED AS THERE WERE LESS THAN')
print('3 TRIALS IN THE GROUP, CAUSING A NaN VALUE FOR THE T-TEST CALCULATIONS:')
print("")
print(df_behavstats[df_behavstats.isna().any(axis=1)].index)
df_behavstats = df_behavstats[pd.notnull(df_behavstats['switch_rt'])]
print("")
print("")

df_behavstats.to_csv('RT_with_stats_and_switches.csv')


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# T-TESTS AND WRITING TO .TXT
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

mean   = df_behavstats['mean_rt'] 
SD     = df_behavstats['SD_rt'] 
MAD    = df_behavstats['MAD_rt']
median = df_behavstats['median_rt'] 

rt1    = df_behavstats['rt_trial_1']
rt2    = df_behavstats['rt_trial_2']
rt3    = df_behavstats['rt_trial_3']
rt123  = df_behavstats['switch_rt']


a = stats.ttest_ind(mean, rt1)
b = stats.ttest_ind(mean, rt2)
c = stats.ttest_ind(mean, rt3)
MEANvsAVRT = stats.ttest_ind(mean, rt123)

d = stats.ttest_ind(median, rt1)
e = stats.ttest_ind(median, rt2)
f = stats.ttest_ind(median, rt3)
MEDvsAVRT = stats.ttest_ind(median, rt123) 

standard_t_tests = [a,b,c,MEANvsAVRT,d,e,f,MEDvsAVRT]


a1 = stats.ttest_ind(mean, rt1, equal_var = False)
b1 = stats.ttest_ind(mean, rt2, equal_var = False)
c1 = stats.ttest_ind(mean, rt3, equal_var = False)
MEANvsAVRT1 = stats.ttest_ind(mean, rt123, equal_var = False)

d1 = stats.ttest_ind(median, rt1, equal_var = False)
e1 = stats.ttest_ind(median, rt2, equal_var = False)
f1 = stats.ttest_ind(median, rt3, equal_var = False)
MEDvsAVRT1 = stats.ttest_ind(median, rt123, equal_var = False) 

welchs_t_tests = [a1,b1,c1,MEANvsAVRT1,d1,e1,f1,MEDvsAVRT1]


t_data = {'standard':standard_t_tests, 'welchs':welchs_t_tests}
t_rows = ['mean_vs_rt1', 'mean_vs_rt2', 'mean_vs_rt3', 'mean_vs_rt123', 'med_vs_rt1', 'med_vs_rt2', 'med_vs_rt3', 'med_vs_rt123']

df_t_tests = pd.DataFrame(data=t_data, index=t_rows)
df_t_tests.to_csv('RT_t_tests.csv')


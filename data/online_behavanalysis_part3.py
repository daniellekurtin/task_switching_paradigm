import pandas as pd
import numpy as np
from scipy import integrate, stats
from numpy import absolute, mean  
from itertools import islice
import statsmodels.api as sm
from statsmodels.formula.api import ols
import statsmodels.stats.multicomp
import seaborn as sns
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf
import os 

## Note: MAD isn't working; can come back to it later. See behavanalysis_part3 line 50 for examples
## This calculates 2 different ways of looking at reaction time: the first trial after a switch, "first_switch_trial", 
# and the average of the first three switch trials, "average_switch_trial."


def create_df3(raw_data_location3):
    
    raw_data_location3 = open(r'C:\Users\danie\Documents\SURREY\Project_1\TaskSwitchingParadigm\online_TSP\second_online_cohort\pilot2_withoccurence.csv')
    path = (r'C:\Users\danie\Documents\SURREY\Project_1\TaskSwitchingParadigm\online_TSP\second_online_cohort')

    df = pd.read_csv(raw_data_location3, header = 0)

    df_behavstats = pd.DataFrame()
    df_behavstats1 = pd.DataFrame()   
    df_behavstats2 = pd.DataFrame()
    df_behavstats3 = pd.DataFrame()
    df_switch_type = pd.DataFrame()

    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # LOOP WHICH CALCULATES AND CONCATS MAD, SD, MRT, MED
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    df.set_index(['auto_participant_id', 'type', 'occurence'], inplace = True)
    df_switch_type = df
    df_rt = df

    for group_i, group_v in df_rt.groupby(level=[0, 1, 2]):
        group_v = group_v.apply(pd.to_numeric, errors = 'coerce').dropna(how = 'all')
        mask = group_v.index.get_level_values(2)

        mrt = group_v['response_time'].mean()
        SD = group_v['response_time'].std()
        med = group_v['response_time'].median()
        switchtrial0 = group_v['response_time'].iloc[0]

        ## The below can be used if you want to use more than the 1st switch trial to calculate switch cost
        # switchtrial1 = group_v['response_time'].iloc[1]
        # if n > 2:
        #     switchtrial2 = group_v['response_time'].iloc[2]

        group_v.at[group_i, 'mean_rt'] = mrt
        group_v.at[group_i, 'SD_rt'] = SD
        group_v.at[group_i, 'median_rt'] = med
        group_v.at[group_i, 'first_switch_rt'] = switchtrial0

        group_v.reset_index(drop = False, inplace = True)
        df_behavstats1 = pd.concat([df_behavstats1, group_v], sort=False) 

    df_behavstats1.set_index(['auto_participant_id', 'type', 'occurence'], inplace = True)
    df_behavstats1.drop(df_behavstats1.columns[df_behavstats1.columns.str.contains('unnamed',case = False)],axis = 1, inplace = True)



    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # LOOP WHICH CALCULATES AND CONCATS SWITCH RT
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    for group_i, group_v in df_behavstats1.groupby(level=[0, 1, 2]):

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
                group_v.at[index, 'average_switch_rt'] = np.nan

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
            group_v.at[index, 'average_switch_rt'] = j
            
        group_v.reset_index(drop = True, inplace = False)
        df_behavstats = pd.concat([df_behavstats, group_v], sort=True)

    df_behavstats = pd.concat([df_behavstats, df_switch_type.reindex(columns=df.columns)], axis=1)
    df_behavstats = df_behavstats.drop(columns=['response_time'])
    df_behavstats.drop_duplicates(subset="mean_rt", keep='first', inplace=True)

    df_behavstats.drop(df_behavstats.columns[df_behavstats.columns.str.contains('unnamed',case = False)],axis = 1, inplace = True)
 
    # when a group has less than 3 trials in it, the switch_rt is not calculated (m = 0). 
    # if there are NaN values in any of the rows of a column, that column returns NaN as a t-test 
    # value for any t-test calculations it is involved in. therefore i have excluded those rows below:
    print("")
    print("")
    print('BELOW DISPLAYS THE GROUP(S) WHICH HAVE BEEN EXCLUDED AS THERE WERE LESS THAN')
    print('3 TRIALS IN THE GROUP, CAUSING A NaN VALUE FOR THE T-TEST CALCULATIONS:')
    print("")
    print(df_behavstats[df_behavstats.isna().any(axis=1)].index)
    df_behavstats = df_behavstats[pd.notnull(df_behavstats['average_switch_rt'])]
    print("")
    print("")

    df_behavstats.reset_index(drop=False, inplace=True)


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# SWITCH-TYPE COLUMN
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    df_behavstats = df_behavstats.loc[:,~df_behavstats.columns.duplicated()]
    df_behavstats.set_index(['auto_participant_id', 'occurence', 'type'], inplace = True)

    

    for group_index, group_value in df_behavstats.groupby(level=[0, 1]):
        group_value.reset_index(drop = False, inplace = True)
        row_iterator = group_value.iterrows()
        _, previous = next(row_iterator)
        for index, row in group_value.iterrows():

            if np.logical_and(row['changed'] == 1, index == 0):
                if row['type'] == 'ts-trial-digit-span':
                    j = 'NONE-DS'
                if row['type'] == 'ts-trial-spatial-span':
                    j = 'NONE-SS'
                if row['type'] == 'ts-trial-spatial-rotation':
                    j = 'NONE-SR'
                if row['type'] == '':
                    pass
            group_value.at[0, 'switch_type'] = j

        for index, row in row_iterator:
            j = 'none'
            if row['changed'] == 1:
                if row['type'] == 'ts-trial-digit-span' and previous['type'] == 'ts-trial-spatial-span':
                    j = 'SS-DS'
                if row['type'] == 'ts-trial-digit-span' and previous['type'] == 'ts-trial-spatial-rotation':
                    j = 'SR-DS'
                if row['type'] == 'ts-trial-spatial-span' and previous['type'] == 'ts-trial-digit-span':
                    j = 'DS-SS'
                if row['type'] == 'ts-trial-spatial-span' and previous['type'] == 'ts-trial-spatial-rotation':
                    j = 'SR-SS'
                if row['type'] == 'ts-trial-spatial-rotation' and previous['type'] == 'ts-trial-digit-span':
                    j = 'DS-SR'
                if row['type'] == 'ts-trial-spatial-rotation' and previous['type'] == 'ts-trial-spatial-span':
                    j = 'SS-SR'
                if row['type'] == '' and previous['type'] == 'ts-trial-spatial-span':
                    pass
                if row['type'] == '' and previous['type'] == 'ts-trial-spatial-rotation':
                    pass
                if row['type'] == '' and previous['type'] == 'ts-trial-digit-span':
                    pass

                previous = row

            # group_value.reset_index(drop = True, inplace = True)
            group_value.at[index, 'switch_type'] = j
        
        df_behavstats = pd.concat([df_behavstats, group_value], sort=True)
        df_behavstats = df_behavstats.dropna(subset=['switch_type'])
        df_behavstats.to_csv('WithSwitchType.csv')


    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # LMEM
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    md1 = smf.mixedlm("first_switch_rt ~ auto_participant_id ", df_behavstats, groups=df_behavstats["type"])
    mdf1 = md1.fit()
    print('*************************************************************************************')
    print('LINEAR MIXED EFFECTS MODELS')
    print(mdf1.summary())

    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # ANOVAs
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    model = ols(
        'first_switch_rt ~ +C(type)+C(auto_participant_id)+C(switch_type)+C(occurence)+C(occurence):C(type)+C(occurence):C(auto_participant_id)+C(occurence):C(switch_type)+C(type):C(switch_type)+C(auto_participant_id):C(switch_type)+C(type):C(auto_participant_id)',
        data=df_behavstats
        ).fit()
    anova_table = sm.stats.anova_lm(model, typ=2)
    print('*************************************************************************************')
    print('ANOVA TABLE FIRST SWITCH RT')
    print(anova_table)


    model1 = ols(
        'mean_rt  ~ +C(type)+C(auto_participant_id)+C(switch_type)+C(occurence)+C(occurence):C(type)+C(occurence):C(auto_participant_id)+C(occurence):C(switch_type)+C(type):C(switch_type)+C(auto_participant_id):C(switch_type)+C(type):C(auto_participant_id)',
        data=df_behavstats
        ).fit()

    anova_table1 = sm.stats.anova_lm(model1, typ=2)
    print('*************************************************************************************')
    print('ANOVA TABLE MEAN RT')
    print(anova_table1)

    model2 = ols(
        'median_rt  ~ +C(type)+C(auto_participant_id)+C(switch_type)+C(occurence)+C(occurence):C(type)+C(occurence):C(auto_participant_id)+C(occurence):C(switch_type)+C(type):C(switch_type)+C(auto_participant_id):C(switch_type)+C(type):C(auto_participant_id)',
        data=df_behavstats
        ).fit()

    anova_table2 = sm.stats.anova_lm(model2, typ=2)
    print('*************************************************************************************')
    print('ANOVA TABLE MEDIAN SWITCH RT')
    print(anova_table2)


    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # T-TESTS
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    mean   = df_behavstats['mean_rt'] 
    SD     = df_behavstats['SD_rt'] 
    median = df_behavstats['median_rt'] 

    # Check here is mean or median is different from one another; if so, decide which to use. If not, move ahead with one or the other. 
    g1 = stats.ttest_ind(median, mean, equal_var = False) 
    print('*************************************************************************************')
    print('TTEST for difference between mean and median rt: All tasks, all occurences =', g1)
    
    rt1    = df_behavstats['first_switch_rt']
    rt123  = df_behavstats['average_switch_rt']

    f1 = stats.ttest_rel(rt1, rt123)
    print('*************************************************************************************')
    print('TTEST for difference between first and average rt: All tasks, all occurences =', f1)



    df_behavstats.set_index(['auto_participant_id', 'type', 'occurence'], inplace = True)
    
    for group_i, group_v in df_behavstats.groupby(level=[1,2]):
        group_v.reset_index(drop = False, inplace = True)
        for index, row in group_v.iterrows():
                task = group_v['type'].loc[1]
                occurence = group_v['occurence'].loc[1]
                SRT = group_v['first_switch_rt']
                MRT = group_v['average_switch_rt']
                n = len(MRT)
                x = range(0,n,1)
                ttest = stats.ttest_rel(MRT, SRT)
        print('*************************************************************************************')
        print('TASK TYPE=', task, 'OCCURENCE =', occurence)
        print('TTEST BETWEEN FIRST AND AVERAGE RT=', ttest)
        
        fig, axMRT = plt.subplots()
        color = 'tab:red'
        axMRT.set_xlabel('Number of trials')
        axMRT.set_ylabel('Mean RT', color=color)
        axMRT.plot(x, MRT, color=color)
        axMRT.set_ylim([0,3000])
        axMRT.tick_params(axis='y')

        axSRT = axMRT.twinx()  # instantiate a second axes that shares the same x-axis
        color= 'tab:blue'
        axSRT.set_ylabel('Switch RT', color=color)  # we already handled the x-label with ax1
        axSRT.plot(x, SRT, color=color)
        axSRT.set_ylim([0,3000])
        axSRT.tick_params(axis='y')

        t = str(task)
        o = str(occurence)
        name = 'Figures/ScatterPlot for' + t + 'Occurence=' + o +'.jpeg'
        plt.legend(loc='upper left');
        axSRT.text(0, 10, name, bbox={'facecolor': 'wheat', 'alpha': 0.5, 'pad': 10})
        fig.tight_layout()  # otherwise the right y-label is slightly clipped
        fig.savefig(name, dpi=400)








    df_behavstats.reset_index(drop = False, inplace = True)



    # # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # # Testing for learning effects
    # # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # df_behavstats.set_index(['auto_participant_id', 'type', 'occurence'], inplace = True)
    
    # for group_i, group_v in df_behavstats.groupby(level=[1,2]):
    #     group_v.reset_index(drop = False, inplace = True)
    #     last_occ = []
    #     first_occ = []
    #     for index, row in group_v.iterrows():
    #             if group_v['occurence'].loc[1] == 8 :
    #                 last_occ = group_v['average_switch_rt']
    #                 print('last_occ',last_occ)
    #             elif group_v['occurence'].loc[1] == 0 :
    #                 first_occ = group_v['average_switch_rt']
    #                 print('first_occ',first_occ)
    #             else:
    #                 continue
    #             task = group_v['type'].loc[1]
    #             occurence = group_v['occurence'].loc[1]
    #             ttest = stats.ttest_rel(last_occ, first_occ)
    #     print('*************************************************************************************')
    #     print('TASK TYPE=', task, 'OCCURENCE =', occurence)
    #     print('TTEST BETWEEN FIRST LAST AVERAGE RT=', ttest)
    # df_behavstats.reset_index(drop = False, inplace = True)


    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # Plots!
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    ax1 = sns.boxplot(x='type', y='mean_rt', data=df_behavstats)
    ax1 = sns.swarmplot(x='type', y='mean_rt', data=df_behavstats, color=".25")
    figure1 = ax1.get_figure()    
    figure1.savefig('Figures/boxplot_Mean_ShowDataPoints.png', dpi=400)
    plt.close()

    ax2 = sns.boxplot(x='type', y='mean_rt', hue='occurence', data=df_behavstats)
    figure2 = ax2.get_figure()    
    figure2.savefig('Figures/boxplot_Mean_byTaskType.png', dpi=400)
    plt.close()

    ax3 = sns.boxplot(x='type', y='first_switch_rt', data=df_behavstats)
    ax3 = sns.swarmplot(x='type', y='first_switch_rt', data=df_behavstats, color=".25")
    figure3 = ax3.get_figure()    
    figure3.savefig('Figures/boxplot_Switch_ShowDataPoints.png', dpi=400)
    plt.close()

    ax4 = sns.boxplot(x='type', y='first_switch_rt', hue='occurence', data=df_behavstats)
    figure4 = ax4.get_figure()    
    figure4.savefig('Figures/boxplot_Switch_byTaskType.png', dpi=400)
    plt.close()

    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # Write ttests to a .csv file
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # a = stats.ttest_ind(mean, rt1)
    # MEANvsAVRT = stats.ttest_ind(mean, rt123)

    # d = stats.ttest_ind(median, rt1)
    # MEDvsAVRT = stats.ttest_ind(median, rt123) 

    # standard_t_tests = [a,MEANvsAVRT,d,MEDvsAVRT]

    # a1 = stats.ttest_ind(mean, rt1, equal_var = False)
    # MEANvsAVRT1 = stats.ttest_ind(mean, rt123, equal_var = False)

    # d1 = stats.ttest_ind(median, rt1, equal_var = False)
    # MEDvsAVRT1 = stats.ttest_ind(median, rt123, equal_var = False) 

    # welchs_t_tests = [a1,MEANvsAVRT1,d1,MEDvsAVRT1]


    # t_data = {'standard':standard_t_tests, 'welchs':welchs_t_tests}
    # t_rows = ['mean_vs_rt1', 'mean_vs_rt123', 'med_vs_rt1', 'med_vs_rt123']

    # df_t_tests = pd.DataFrame(data=t_data, index=t_rows)
    # name='TTests.csv'
    # dest = os.path.join(path, name)
    # df_t_tests.to_csv(dest)


    return df_behavstats
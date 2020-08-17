import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from pathlib import Path
from itertools import islice

class My_dict(dict):
    def __init__(self):
        self = dict()
    def add(self, key, value):
        self[key] = value



class Df():
    def __init__(self, raw_data_location):
        df = pd.read_csv(raw_data_location, header = 0)
        self.df = df

    
    def tsp_df(self):
        df = self.df
        df1 = pd.DataFrame()
        for pid, g in df.groupby(['auto_participant_id']):
            g['index_raw'] = g.index
            n = 0
            for i, r in g.iterrows():
                n = n + 1
                g.at[i, 'index_raw'] = n
            df1 = pd.concat([df1, g], sort=False) 

        df1.rename(columns= {
            "trial_task_type":"type", 
            "answer_index":"target_ans",
            "response_answer":"participant_ans",
            "response_enabled_time":"time_response_enabled",
            "response_time":"time_response_submitted",    
            "stimulus_on":"time_start",
            "response_correct":"accuracy",
            }, inplace=True
            ) 
    
        # delete all columns but these
        df1 = df1[[
            'index_raw',
            'auto_participant_id',
            'participant_age',
            'participant_gender',
            'type',
            'trial_type',
            'trial_index',
            'time_elapsed',
            'time_start',
            'time_response_enabled',
            'time_response_submitted',
            'participant_ans',
            'target_ans',
            'accuracy'
        ]]

        self.df = df1

    def tsp_scan(self):
        df = self.df
        # determine how many nonanswered trials were there
        xx = (len(df['participant_ans']))
        #drops non-answered trials
        df = df[~df['participant_ans'].isnull()]
        yy = (len(df['participant_ans']))

        # number of trials missed
        zz = xx - yy

        # number of trials missed as a % out of total
        vv = zz / xx * 100
        vv = int(vv)

        no_participants = df['auto_participant_id'].nunique()

        df = df.drop_duplicates(subset='auto_participant_id', keep='last', inplace=False)
        mean_age = df['participant_age'].mean()
        mean_age = int(mean_age)

        xx = df['participant_gender'].value_counts()

        gender = {}
        gender_two = {'M':0, 'F':0}
        for field, value in xx.iteritems():
            gender[field] = value
        for index in gender:
            male = index.lower() == 'male'
            female = index.lower() == 'female'
            if male==True: 
                gender_two['M'] = gender_two['M'] + gender[index]
            if female==True:
                gender_two['F'] = gender_two['F'] + gender[index]

        details = {'no_missed_trials':zz,'percent_trials_missed':vv,'no_participants':no_participants,'mean_age':mean_age,'no_genders':gender_two}
    
        self.stack = details

    def tsp_struct(self):
        df = self.df

        df1 = pd.DataFrame()
        df2 = pd.DataFrame()
        df3 = pd.DataFrame()
        df4 = pd.DataFrame()
        df5 = pd.DataFrame()


        # 'changed' column
        df['response_time'] = np.where((
            df['trial_type'] == 'ts-trial') & (df['time_response_submitted'] == np.nan), 3,
            df['time_response_submitted'].sub(df['time_response_enabled'], axis=0)
            )


        for index, row in df.iterrows():
            if row['trial_type'] == 'ts-info-card':
                df.at[index, 'changed'] = 1
            else:
                df.at[index, 'changed'] = 0
            
        df1 = df
        
        df1['changed_shifted'] = df1['changed'].shift(1)
        df2 = df1.drop(columns = ['changed'])
        
        # # 'block' column
        # for gi, gv in df1.groupby(['auto_participant_id']):
        #     j = 1
        #     for index1, row1 in gv.iterrows():
        #         if row1['trial_type'] == 'ts-block-break':
        #             j = j + 1    
        #         else:
        #             j = j    
        #         gv.at[index1, 'block'] = j

        #     df2 = pd.concat([df2, gv], sort=False)


        # 'switchtype' column
        for gri, grv in df2.groupby(['auto_participant_id']):
            for indx, rowx in grv['trial_type'].iteritems():
                if rowx == 'ts-trial':
                    continue
                else:
                    grv.drop(indx, inplace=True)
            df3 = pd.concat([df3, grv], sort=False)

        for rindex, rgroup in df3.groupby(['auto_participant_id']):
            rgroup.sort_values('index_raw')
            for index, row in rgroup.iterrows():
                if np.logical_and(row['changed_shifted'] == 1, row['index_raw'] == 2):
                    if row['type'] == 'ts-trial-digit-span':
                        st = 'NONE-DS'
                    if row['type'] == 'ts-trial-spatial-span':
                        st = 'NONE-SS'
                    if row['type'] == 'ts-trial-spatial-rotation':
                        st = 'NONE-SR'
                rgroup.at[index, 'switch_type'] = str(st)

            row_iterator = rgroup.iterrows()
            _, previous = next(row_iterator)
            for index, row in row_iterator:
                st = 'none'
                if row['changed_shifted'] == 1:
                    if row['type'] == 'ts-trial-digit-span' and previous['type'] == 'ts-trial-spatial-span':
                        st = 'SS-DS'
                    if row['type'] == 'ts-trial-digit-span' and previous['type'] == 'ts-trial-spatial-rotation':
                        st = 'SR-DS'
                    if row['type'] == 'ts-trial-spatial-span' and previous['type'] == 'ts-trial-digit-span':
                        st = 'DS-SS'
                    if row['type'] == 'ts-trial-spatial-span' and previous['type'] == 'ts-trial-spatial-rotation':
                        st = 'SR-SS'
                    if row['type'] == 'ts-trial-spatial-rotation' and previous['type'] == 'ts-trial-digit-span':
                        st = 'DS-SR'
                    if row['type'] == 'ts-trial-spatial-rotation' and previous['type'] == 'ts-trial-spatial-span':
                        st = 'SS-SR'
                    if row['type'] == 'ts-trial-spatial-span' and previous['type'] == 'ts-trial-spatial-span':
                        pass
                    if row['type'] == 'ts-trial-spatial-rotation' and previous['type'] == 'ts-trial-spatial-rotation':
                        pass
                    if row['type'] == 'ts-trial-spatial-span' and previous['type'] == 'ts-trial-digit-span':
                        pass

                    previous = row

                rgroup.at[index, 'switch_type'] = str(st)
            
            df4 = pd.concat([df4, rgroup], sort=False)


        # 'occurence' column
        for group_index, group_value in df4.groupby(['auto_participant_id', 'type']):
            k = 0
            for iindex, rrow in group_value.iterrows():
                if rrow['changed_shifted'] == 1:
                    k = k + 1
                else:
                    k = k
                group_value.at[iindex, 'occurence'] = k

            df5 = pd.concat([df5, group_value], sort=False)
        
        df5 = df5.drop(columns=['time_response_submitted', 'time_response_enabled', 'time_elapsed'])
        
        self.df = df5



    def tsp_mrt(self):
        df = self.df
        df = df.set_index(['auto_participant_id', 'type', 'occurence'])
        RTs = My_dict()
        # mean response time (mrt) calc. for each occurence per type
        for title, df_mrt1 in df.groupby(level=[0,1,2]):
            df_mrt1 = df_mrt1.apply(pd.to_numeric, errors = 'coerce').dropna(how = 'all')
            
            mrt = df_mrt1['response_time'].mean()
            SD = df_mrt1['response_time'].std()
            med = df_mrt1['response_time'].median()
            srt = df_mrt1['response_time'].iloc[0]

            # print('For',title,':')
            # print('MRT=', mrt, 'SD=', SD, 'MED RT=', med, 'SWITCH RT=', srt)
            # print('****************************************************************************************')

        #Need to create an array w/ the values calculated above
            a = np.array([mrt, med, SD, srt])

            for indexx, roww in df_mrt1.iterrows():
                RTs.key = indexx
                RTs.value = a
                RTs.add(RTs.key, RTs.value)
        # This stays indented here! :) 
        self.RTs = RTs



    def tsp_switchrt(self):
        df = self.df
        df1 = pd.DataFrame()
        df2 = pd.DataFrame()
        df3 = pd.DataFrame()

        for group_i, group_v in df.groupby(['type', 'occurence']):

            for index, row in group_v['response_time'].iteritems():
                if pd.notnull(row):
                    continue
                else:
                    group_v.at[index, 'response_time'] = np.NaN
            df1 = pd.concat([df1, group_v], sort=False)

        for gi, gv in df1.groupby(['type', 'occurence']):
            n = 0
            for index, row in gv.iterrows():
                n =  n + 1
            # ----- can change to % of trials ( m = x% of n) -----
            # here dicates over how many trials the RT is averaged over (m), dependant on how many 
            # trials are in the overall group (n).
            ##
            # eg, when the number of overall trials in the group is less than 3 (if n < 3), then 
            # the number of trials to average over is 0 (m = 0), and the rows are left empty (np.nan).
            if n < 3:
                m = 1
                for i, r in gv.iterrows():
                    gv.at[i, 'first_switch_rt'] = np.NaN

            elif n >= 3 and n < 5:
                m = 1
            elif n >= 5:
                m = 1
        
            number_of_trials = 0
            overall_rt = 0
            # the 'islice' tells pandas to iterate with iterrows over the first 'm' rows
            for ind, ro in islice(gv.iterrows(), m):
                number_of_trials = number_of_trials + 1    
                overall_rt = overall_rt + ro['response_time']     
                j = (overall_rt/number_of_trials)
                gv.at[index, 'first_switch_rt'] = j
            df2 = pd.concat([df2, gv], sort=False)
        
        self.df = df2

        # when a group has less than 3 trials in it, the switch_rt is not calculated (m = 0). 
        # if there are NaN values in any of the rows of a column, that column returns NaN as a t-test 
        # value for any t-test calculations it is involved in. therefore i have excluded those rows below:
        for gri, grv in df2.groupby(['type', 'occurence']):
            for indx, rowx in grv['first_switch_rt'].iteritems():
                if pd.notnull(rowx):
                    continue
                else:
                    grv.drop(indx, inplace=True)
            df3 = pd.concat([df3, grv], sort=False)

        df4 = df3.set_index(['type', 'occurence'])

        first_switch_rt = My_dict()

        for indexx, roww in df4.iterrows():
            first_switch_rt.key = indexx
            first_switch_rt.value = roww['first_switch_rt']
            first_switch_rt.add(first_switch_rt.key, first_switch_rt.value)

        self.first_switch_rt = first_switch_rt

# Calculate Accuracy
    def tsp_accuracy(self):
        df = self.df
        df = df.set_index(['auto_participant_id', 'type', 'occurence'])

        #OVERALL % ACC
        number_correct = df['accuracy'].sum() 
        number_of_trials = df['participant_ans'].count()
        overall_accuracy = (number_correct / number_of_trials) * 100
        print('OVERALL ACCURACY =', overall_accuracy)

        ACC = My_dict()
        #GROUPED % ACC
        for group_i, group_v in df.groupby(level=[0,1,2]):
            for gi, gv in group_v.iterrows():
                overall_accuracy = 0
                corr = group_v['accuracy'].sum() 
                total = len(group_v['accuracy'])
                overall_accuracy = (corr / total) * 100
                a = np.array([overall_accuracy])

                for indexx, roww in group_v.iterrows():
                    ACC.key = indexx
                    ACC.value = a
                    ACC.add(ACC.key, ACC.value)

            self.ACC = ACC
            


        # print("MIXED EFFECTS*************************************************************************************")
        # md1 = smf.mixedlm("first_switch_rt ~ switch_type + occurence + auto_participant_id ", df_behavstats, groups=df_behavstats["auto_participant_id"])
        # mdf1 = md1.fit()
        # print(mdf1.summary())
        # print("*************************************************************************************")
                


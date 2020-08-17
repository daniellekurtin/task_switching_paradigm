import pandas as pd
import numpy as np
import os

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
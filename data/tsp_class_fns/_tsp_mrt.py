import pandas as pd
import numpy as np
import os
from .HelperClasses import My_dict

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
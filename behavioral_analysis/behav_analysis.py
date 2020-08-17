import pandas as pd
import os
import Classes.class_df
from Classes.class_df import Df, My_dict

### 1. using Df Class for TSP

## paramaters
dirname = os.path.dirname(__file__)
raw_data_location = os.path.join(dirname, 'data/data_clean.csv')

## 1.0 __init__: initialise TSP instance of class Df, and call it 'TSP_df'
# returns: df
TSP_df = Df(raw_data_location)
    # save: raw pd.DataFrame created as .csv
TSP_df.df.to_csv(os.path.join(dirname, 'data/class_dfs/df_tsp_raw.csv'))


## 1.1 Df.transform: the df into TSP format (method 'tsp_df')
# returns: df
TSP_df.tsp_df()


## 1.2 Df.stack: scan df for metrics
# returns: df; 'stack' dict
TSP_df.tsp_scan()
    # save: TSP .csv
TSP_df.df.to_csv(os.path.join(dirname, 'data/class_dfs/df_tsp.csv'))
    # check:
# for col in TSP_df.df.columns:
#     print(col)
    # dict: stack
print("raw tsp stack:")
print(TSP_df.stack)


## 1.3 Df.transform: switch type, block, occurence (method 'tsp_struct')
# returns: df
TSP_df.tsp_struct()
    # save: st, occ, block .csv
TSP_df.df.to_csv(os.path.join(dirname, 'data/class_dfs/df_tsp_structured.csv'))
    # check:
# for col in TSP_df.df.columns:
#     print(col)


## 1.4 Df.transform: mrt (from 'online_behavanalysis_part1.py')
# returns: 'mrt' dict
# TSP_df.tsp_mrt()
# print(TSP_df.RTs)


## 1.5 Df.transform: switch reaction time
# returns: 'first_switch_rt' dict
# TSP_df.tsp_switchrt()
#     # check:
# print("first switch rt's for each t, o:")
# print(TSP_df.first_switch_rt)

## 1.6 Determine accuracy
TSP_df.tsp_accuracy()
print(TSP_df.ACC)
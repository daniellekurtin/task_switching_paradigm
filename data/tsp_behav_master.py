import pandas as pd
import os
from Df_main_class import Df


### 1. using Df Class for TSP

## paramaters
dirname = os.path.dirname(__file__)
raw_data_location = os.path.join(dirname, 'data_clean.csv')

## 1.0 __init__: initialise TSP instance of class Df, and call it 'TSP_df'
TSP_df = Df(raw_data_location)
#TSP_df.df.to_csv(os.path.join(dirname, 'processed_dfs/df_tsp_raw.csv'))


## 1.1 Df.transform: the df into TSP format (method 'tsp_df')
TSP_df.tsp_df()


## 1.2 Df.stack: scan df for metrics
TSP_df.tsp_scan()
#TSP_df.df.to_csv(os.path.join(dirname, 'processed_dfs/df_tsp.csv'))
# for col in TSP_df.df.columns:
#     print(col)
print("raw tsp stack:")
print(TSP_df.stack)


## 1.3 Df.transform: switch type, block, occurence (method 'tsp_struct')
TSP_df.tsp_struct()
#TSP_df.df.to_csv(os.path.join(dirname, 'processed_dfs/df_tsp_structured.csv'))
# for col in TSP_df.df.columns:
#     print(col)


## 1.4 Df.transform: mrt (from 'online_behavanalysis_part1.py')
# returns: 'mrt' dict
TSP_df.tsp_mrt()
# print(TSP_df.mrt)


## 1.5 Df.transform: switch reaction time
TSP_df.tsp_switchrt()
#TSP_df.df.to_csv(os.path.join(dirname, 'processed_dfs/df_tsp_switchrt.csv'))
print("first switch rt's for each p, t, b, o:")
print(TSP_df.first_switch_rt)


## 1.6 Determine accuracy
TSP_df.tsp_accuracy()
print(TSP_df.ACC)


## 1.7 Statistical tests
#TSP_df.tsp_stats()

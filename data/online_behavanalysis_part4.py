import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns 
import os 
from scipy import integrate, stats
from numpy import absolute, mean  
from pandas import DataFrame
from itertools import islice
import seaborn as sns
import statsmodels.api as sm
from statsmodels.formula.api import ols
import statsmodels.stats.multicomp


def create_df4(raw_data_location4):
    raw_data_location4 = open(r'C:\Users\danie\Documents\SURREY\Project_1\TaskSwitchingParadigm\online_TSP\second_online_cohort\pilot2_WithSwitchCosts.csv')   
    path = (r'C:\Users\danie\Documents\SURREY\Project_1\TaskSwitchingParadigm\online_TSP\second_online_cohort')

    df_accuracy = pd.read_csv(raw_data_location4, header = 0)
    df_accuracy1 = pd.DataFrame()


        #OVERALL % ACC
    df_accuracy.set_index(['auto_participant_id', 'type', 'occurence'], inplace = True)
    number_correct = df_accuracy['accuracy'].sum() 
    number_of_trials = df_accuracy['first_switch_rt'].count()
    overall_accuracy = (number_correct / number_of_trials) * 100
    print('*************************************************************************************')
    print('OVERALL ACCURACY=',overall_accuracy)
    
    

        #GROUPED % ACC

    for group_i, group_v in df_accuracy.groupby(level=[1, 2]):

        overall_accuracy = 0
        for index, row in group_v:
                corr = group_v['accuracy'].sum() 
                total = group_v['accuracy'].size
                overall_accuracy = (corr / total) * 100
        print('*************************************************************************************')
        print(index,'OVERALL ACCURACY=',overall_accuracy, 'Number CORR=',corr, 'Total=',total)


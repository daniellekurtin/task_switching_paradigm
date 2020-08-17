import pandas as pd
import numpy as np
import os

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
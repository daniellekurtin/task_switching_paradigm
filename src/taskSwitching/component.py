import numpy as np
from psychopy import visual, clock, event
from math import floor, ceil
from random import randint, shuffle
from datetime import datetime


class Component:
    """
    Any set of screens in the experiment is a component. These could be trials, instructions, breaks, etc.
    """
    logEntries = []

    def __init__(self, experiment, **kwargs):
        """
        :type experiment: Experiment
        :param kwargs:
        """
        if experiment is None:
            raise ValueError('experiment must be specified')
        self.experiment = experiment

        for k in kwargs.keys():
            self.__setattr__(k, kwargs[k])

    def log(self, entry, level='INFO'):
        """
        Write a log entry for this component
        :param entry: text to log
        :type entry: str
        :param level: notification level for entry
        :type level: str
        :return:
        """
        self.logEntries.append(str(datetime.now()) + ': ' + level + ' - ' + entry)


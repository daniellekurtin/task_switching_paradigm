import numpy as np
from psychopy import visual, clock, event
from math import floor, ceil
from random import randint, shuffle
from datetime import datetime
import json
from taskSwitching import grid
from psychopy.logging import _levelNames as levels


class Component:
    """
    Any set of screens in the experiment is a component. These could be trials, instructions, breaks, etc.
    """

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

        self.logEntries = []

    def log(self, entry, level='INFO'):
        """
        Write a log entry for this component
        :param entry: text to log
        :type entry: str
        :param level: notification level for entry
        :type level: str
        :return:
        """
        self.logEntries.append({
            'TIME': datetime.now(),
            'LEVEL': level,
            'LOG': entry
        })

    def run(self):
        """
        Components should overwrite the main method to implement themselves
        :return:
        """
        self.prepare()
        self.main()
        self.cleanup()

    def prepare(self):
        self.log('Begin')

    def main(self):
        pass

    def cleanup(self):
        log_level = self.experiment.log_level # to_json removes experiment
        self.log(self.to_json(),level='DEBUG')
        print("\n")
        for log in self.logEntries:
            if levels[log['LEVEL']] >= levels[log_level]:
                print('{}: {} - {}'.format(str(log['TIME']), log['LEVEL'], log['LOG']))

    def to_json(self, o=None):
        """
        :param o: object to stringify (self by default)
        :return: JSON string representation of the Component
        """
        if o is None:
            d = self.__dict__
        else:
            try:
                # Dump out early if this is not the kind of object we want to record details of
                if not isinstance(o, (
                    Component,
                    grid.Grid,
                    visual.Rect,
                    visual.TextStim
                )):
                    return str(o)
                d = o.__dict__
            except AttributeError:
                return o

        out = {}

        if 'experiment' in d.keys():
            d.pop('experiment')

        for k in d.keys():
            if isinstance(d[k], object):
                if (not isinstance(d[k], (dict, set, str, int, float, bool))) and d[k] is not None:
                    out[k] = self.to_json(d[k])
                elif isinstance(d[k], np.ndarray):
                    out[k] = d[k].tolist()
                else:
                    out[k] = d[k]

        if o is not None:
            return out

        return json.dumps(out)

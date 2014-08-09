from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import sys
import numpy as np
import pandas as pd
import matplotlib.cbook as cbook

from ggplot import scales
from ggplot.utils import is_categorical, make_iterable_ntimes
from ggplot.utils.exceptions import GgplotError
from .stat import stat

import datetime
import time

_MSG_YVALUE = """A variable was mapped to y.
    stat_bin sets the y value to the count of cases in each group.
    The mapping to y was ignored.
    If you want y to represent values in the data, use stat="bar".
"""

_MSG_BINWIDTH = """stat_bin: binwidth defaulted to range/30.
    Use 'binwidth = x' to adjust this.
"""


class stat_bin(stat):
    REQUIRED_AES = {'x'}
    DEFAULT_PARAMS = {'geom': 'histogram', 'position': 'stack',
                      'width': 0.9, 'drop': False, 'right': False,
                      'binwidth': None, 'origin': None, 'breaks': None,
                      'labels': None}
    CREATES = {'y', 'width'}


    def _calculate_global(self, data):
        # Calculate breaks if x is not categorical
        binwidth = self.params['binwidth']
        self.breaks = self.params['breaks']
        right = self.params['right']
        x = data['x'].values

        # For categorical data we set labels and x-vals
        if is_categorical(x):
            labels = self.params['labels']
            if labels == None:
                labels = sorted(set(x))
            self.labels = labels
            self.length = len(self.labels)

        # For non-categoriacal data we set breaks
        if not (is_categorical(x) or self.breaks):
            # Check that x is numerical
            if isinstance(x[0], datetime.date):
                def convert(d):
                    d = datetime.datetime.combine(d, datetime.datetime.min.time())
                    return time.mktime(d.timetuple())
                x = [convert(d) for d in x]
            elif isinstance(x[0], datetime.datetime):
                x = [time.mktime(d.timetuple()) for d in x]
            elif isinstance(x[0], datetime.time):
                raise GgplotError("Cannot recognise the type of x")
            elif not cbook.is_numlike(x[0]):
                raise GgplotError("Cannot recognise the type of x")
            if binwidth is None:
                _bin_count = 30
                self._print_warning(_MSG_BINWIDTH)
            else:
                _bin_count = int(np.ceil(np.ptp(x))) / binwidth
            _, self.breaks = pd.cut(x, bins=_bin_count, labels=False,
                                        right=right, retbins=True)
            self.length = len(self.breaks)


    def _calculate(self, data):
        x = data.pop('x')
        right = self.params['right']

        # y values are not needed
        try:
            del data['y']
        except KeyError:
            pass
        else:
            self._print_warning(_MSG_YVALUE)

        if isinstance(x[0], datetime.date):
            def convert(d):
                d = datetime.datetime.combine(d, datetime.datetime.min.time())
                return time.mktime(d.timetuple())
            x = x.apply(convert)
            self.dtype = datetime.date

        # If weight not mapped to, use one (no weight)
        try:
            weights = data.pop('weight')
        except KeyError:
            weights = np.ones(len(x))
        else:
            weights = make_iterable_ntimes(weights, len(x))

        if is_categorical(x.values):
            x_assignments = x
            x = self.labels
            width = make_iterable_ntimes(self.params['width'], self.length)
        elif cbook.is_numlike(x.iloc[0]):
            x_assignments = pd.cut(x, bins=self.breaks, labels=False,
                                           right=right)
            width = np.diff(self.breaks)
            x = [self.breaks[i] + width[i] / 2
                 for i in range(len(self.breaks)-1)]
        else:
            raise GgplotError("Cannot recognise the type of x")

        # Create a dataframe with two columns:
        #   - the bins to which each x is assigned
        #   - the weights of each x value
        # Then create a weighted frequency table
        _df = pd.DataFrame({'assignments': x_assignments,
                            'weights': weights
                            })
        _wfreq_table = pd.pivot_table(_df, values='weights',
                                      rows=['assignments'], aggfunc=np.sum)

        # For numerical x values, empty bins get have no value
        # in the computed frequency table. We need to add the zeros and
        # since frequency table is a Series object, we need to keep it ordered
        try:
            empty_bins = set(self.labels) - set(x_assignments)
        except:
            empty_bins = set(range(len(width))) - set(x_assignments)
        _wfreq_table = _wfreq_table.to_dict()
        for _b in empty_bins:
            _wfreq_table[_b] = 0
        _wfreq_table = pd.Series(_wfreq_table).sort_index()

        y = list(_wfreq_table)
        new_data = pd.DataFrame({'x': x, 'y': y, 'width': width})

        # Copy the other aesthetics into the new dataframe
        n = len(x)
        for ae in data:
            new_data[ae] = make_iterable_ntimes(data[ae].iloc[0], n)
        return new_data



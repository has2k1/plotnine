from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import sys
import numpy as np
import pandas as pd
import matplotlib.cbook as cbook

from ggplot.utils import is_categorical, make_iterable_ntimes
from .stat import stat

_MSG1 = """A variable was mapped to y.
    stat_bin sets the y value to the count of cases in each group.
    The mapping to y was ignored.
    If you want y to represent values in the data, use stat="identity".
"""

_MSG2 = """stat_bin: binwidth defaulted to range/30.
    Use 'binwidth = x' to adjust this.
"""


class stat_bin(stat):
    REQUIRED_AES = {'x'}
    DEFAULT_PARAMS = {'geom': 'bar', 'position': 'stack',
                      'width': 0.9, 'drop': False, 'right': False,
                      'binwidth': None, 'origin': None, 'breaks': None}
    CREATES = {'y', 'width'}

    _warnings_printed = set()

    def _print_warning(self, message, message_id):
        """
        Prints message to the standard error.

        message_id ensures that the message is printed once
        """
        if message_id not in self._warnings_printed:
            sys.stderr.write(message)
            self._warnings_printed.add(message_id)

    def _calculate(self, data):
        x = data.pop('x')
        breaks = self.params['breaks']
        right = self.params['right']
        binwidth = self.params['binwidth']

        # y values are not needed
        try:
            del data['y']
        except KeyError:
            pass
        else:
            self._print_warning(_MSG1, 1)

        # TODO: make sure it is passed from the geom
        # data.pop('weight')
        weight = 1
        x_weights = np.ones(len(x)) * weight

        categorical = is_categorical(x.values)
        if categorical:
            x_assignments = x
            x = sorted(set(x))
            width = make_iterable_ntimes(self.params['width'], len(x))
        elif cbook.is_numlike(x.iloc[0]):
            if breaks is None and binwidth is None:
                _bin_count = 30
                self._print_warning(_MSG1, 1)
            if binwidth:
                _bin_count = int(np.ceil(np.ptp(x))) / binwidth

            # Breaks have a higher precedence and,
            # pandas accepts either the breaks or the number of bins
            _bins_info = breaks or _bin_count
            x_assignments, breaks = pd.cut(x, bins=_bins_info, labels=False,
                                           right=right, retbins=True)
            width = np.diff(breaks)
            x = [breaks[i] + width[i] / 2
                 for i in range(len(breaks)-1)]
        else:
            # TODO: Create test case
            raise Exception("Cannot recognise the type of x")

        # Create a dataframe with two columns:
        #   - the bins to which each x is assigned
        #   - the weights of each x value
        # Then create a weighted frequency table
        _df = pd.DataFrame({'assignments': x_assignments,
                            'weights': x_weights
                            })
        _wfreq_table = pd.pivot_table(_df, values='weights',
                                      rows=['assignments'], aggfunc=np.sum)

        # For numerical x values, empty bins get have no value
        # in the computed frequency table. We need to add the zeros and
        # since frequency table is a Series object, we need to keep it ordered
        if len(_wfreq_table) < len(x):
            empty_bins = set(range(max(x_assignments))) - set(x_assignments)
            for _b in empty_bins:
                _wfreq_table[_b] = 0
            _wfreq_table = _wfreq_table.sort_index()

        y = list(_wfreq_table)
        new_data = pd.DataFrame({'x': x, 'y': y, 'width': width})

        # Copy the other aesthetics into the new dataframe
        n = len(x)
        for ae in data:
            new_data[ae] = make_iterable_ntimes(data[ae].iloc[0], n)
        return new_data


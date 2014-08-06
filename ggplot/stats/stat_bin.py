from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import sys
import numpy as np
import pandas as pd
import matplotlib.cbook as cbook
import pandas.core.common as com

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

    def _calculate(self, data, scales, **kwargs):
        x = data['x']
        breaks = self.params['breaks']
        right = self.params['right']
        binwidth = self.params['binwidth']
        range_ = scales.x.dimension((0, 0))

        # y values are not needed
        if 'y' in data:
            self._print_warning(_MSG_YVALUE)

        if len(x) > 0 and isinstance(x.get(0), datetime.date):
            def convert(d):
                d = datetime.datetime.combine(d, datetime.datetime.min.time())
                return time.mktime(d.timetuple())
            x = x.apply(convert)
        elif len(x) > 0 and isinstance(x.get(0), datetime.datetime):
            x = x.apply(lambda d: time.mktime(d.timetuple()))
        elif len(x) > 0 and isinstance(x.get(0), datetime.time):
            raise GgplotError("Cannot recognise the type of x")

        # If weight not mapped to, use one (no weight)
        try:
            weights = data['weight']
        except KeyError:
            weights = np.ones(len(x))
        else:
            weights = np.array(
                make_iterable_ntimes(weights, len(x)))
            weights[np.isnan(weights)] = 0

        if com.is_integer_dtype(x):
            bins = x
            x = np.sort(x.drop_duplicates())
            width = make_iterable_ntimes(self.params['width'], len(x))
        elif np.diff(range_) == 0:
            bins = x
            width = width
        elif com.is_numeric_dtype(x):
            if breaks is None and binwidth is None:
                bin_count = 30
                self._print_warning(_MSG_BINWIDTH)
            if binwidth:
                bin_count = int(np.ceil(np.ptp(x)) / binwidth)

            # Breaks have a higher precedence and,
            # pandas accepts either the breaks or the number of bins
            bins_info = breaks or bin_count
            bins, breaks = pd.cut(x, bins=bins_info, labels=False,
                                          right=right, retbins=True)
            width = np.diff(breaks)
            x = [breaks[i] + width[i] / 2
                 for i in range(len(breaks)-1)]
        else:
            raise GgplotError("Cannot recognise the type of x")

        # Create a dataframe with two columns:
        #   - the bins to which each x is assigned
        #   - the weights of each x value
        # Then create a weighted frequency table
        df = pd.DataFrame({'bins': bins,
                           'weights': weights})
        wfreq_table = pd.pivot_table(df, values='weights',
                                     rows=['bins'], aggfunc=np.sum)

        # For numerical x values, empty bins get no value
        # in the computed frequency table. We need to add the
        # zeros and since frequency table is a Series object,
        # we need to keep it ordered
        if len(wfreq_table) < len(x):
            empty_bins = set(range(len(x))) - set(bins)
            for b in empty_bins:
                wfreq_table[b] = 0
            wfreq_table = wfreq_table.sort_index()

        res = pd.DataFrame({
            'x' : x,
            'count' : wfreq_table,
            'width' : width})

        # other computed stats
        res['density'] = (res['count'] / width) / res['count'].abs().sum()
        res['ncount'] = res['count'] / res['count'].abs().max()
        res['ndensity'] = res['density'] / res['density'].abs().max()

        return res

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
import pandas as pd
import pandas.core.common as com

from ..utils import make_iterable_ntimes
from ..utils.exceptions import GgplotError, gg_warning
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
                      'binwidth': None, 'origin': None, 'breaks': None}
    DEFAULT_AES = {'y': '..count..'}
    CREATES = {'y', 'width'}

    def _calculate(self, data, scales, **kwargs):
        x = data['x']
        breaks = self.params['breaks']
        right = self.params['right']
        binwidth = self.params['binwidth']
        range_ = scales.x.dimension((0, 0))

        # y values are not needed
        if 'y' in data:
            gg_warning(_MSG_YVALUE)

        if com.is_categorical_dtype(x):
            bins = x.tolist()
            x = x.drop_duplicates().tolist()
            width = make_iterable_ntimes(self.params['width'], len(x))
        elif np.diff(range_) == 0:
            bins = x
            width = make_iterable_ntimes(self.params['width'], len(x))
        elif com.is_numeric_dtype(x):
            mn, mx = range_
            adj = (mx - mn) * 0.001  # .1% of range
            if breaks is None and binwidth is None:
                bin_count = 30
                gg_warning(_MSG_BINWIDTH)
            elif binwidth:
                # create bins over the range like pandas would
                bin_count = int(np.ceil(np.ptp(range_) + adj) / binwidth)
            if breaks is None:
                breaks = np.linspace(mn, mx, bin_count + 1, endpoint=True)
                if right:
                    breaks[0] -= adj
                else:
                    breaks[-1] += adj

            bins = pd.cut(x, bins=breaks, labels=False,
                          right=right)
            width = np.diff(breaks)
            x = [breaks[i] + width[i] / 2
                 for i in range(len(breaks)-1)]
        else:
            raise GgplotError("Cannot recognise the type of x")

        # If weight not mapped to, use one (no weight)
        try:
            weights = data['weight']
        except KeyError:
            weights = np.ones(len(bins))
        else:
            weights = np.asarray(
                make_iterable_ntimes(weights, len(bins)))
            weights[np.isnan(weights)] = 0

        # Create a dataframe with two columns:
        #   - the bins to which each x is assigned
        #   - the weights of each x value
        # Then create a weighted frequency table
        df = pd.DataFrame({'bins': bins,
                           'weights': weights})
        wftable = pd.pivot_table(df, values='weights',
                                 index=['bins'], aggfunc=np.sum)
        # for categorical x
        # Empty bins have NaN value, turn them to zeros
        wftable.fillna(0, inplace=True)

        # For numerical x values, empty bins get no value
        # in the computed frequency table. We need to add the
        # zeros and since frequency table is a Series object,
        # we need to keep it ordered
        if len(wftable) < len(x):
            empty_bins = set(range(len(x))) - set(bins)
            for b in empty_bins:
                wftable[b] = 0
            wftable = wftable.sort_index()
        count = wftable.tolist()

        res = pd.DataFrame({
            'x': x,
            'count': count,
            'width': width})

        # other computed stats
        res['density'] = (res['count'] / width) / res['count'].abs().sum()
        res['ncount'] = res['count'] / res['count'].abs().max()
        res['ndensity'] = res['density'] / res['density'].abs().max()

        return res

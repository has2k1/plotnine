from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
import pandas as pd
import pandas.core.common as com

from ..utils import make_iterable_ntimes
from ..utils.exceptions import GgplotError, gg_warning
from ..scales.utils import fullseq
from .stat import stat

import datetime
import time

_MSG_YVALUE = """A variable was mapped to y.
    stat_bin sets the y value to the count of cases in each group.
    If you want 'y' to represent values in the data, use stat='identity'.
    Or, if you set some aethetics in the ggplot call can do override
    them and this time do not include 'y'
    e.g. stat_bin(aes(x='x')) or geom_bar(aes(x='x'))
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
        origin = self.params['origin']
        range_ = np.asarray(scales.x.dimension((0, 0)))

        # y values are not needed
        if 'y' in data:
            raise GgplotError(_MSG_YVALUE)

        if com.is_categorical_dtype(x):
            bins = x.tolist()
            x = x.drop_duplicates().tolist()
            width = make_iterable_ntimes(self.params['width'], len(x))
        elif np.diff(range_) == 0:
            bins = x
            width = make_iterable_ntimes(self.params['width'], len(x))
        elif com.is_numeric_dtype(x):
            if breaks is None and binwidth is None:
                binwidth = np.ptp(range_) / 30
                gg_warning(_MSG_BINWIDTH)
            if breaks is None:
                if origin is None:
                    breaks = fullseq(range_, binwidth, pad=True)
                else:
                    bincount = np.floor(
                        (range_[1] + 2*binwidth - origin) / binwidth)
                    breaks = np.linspace(
                        origin,
                        range_[1] + binwidth,
                        bincount)

            # fuzzy breaks to protect from floating point rounding errors
            diddle = 1e-07 * np.median(np.diff(breaks))
            if right:
                fuzz = np.hstack(
                    [-diddle, np.repeat(diddle, len(breaks)-1)])
            else:
                fuzz = np.hstack(
                    [np.repeat(-diddle, len(breaks)-1), diddle])

            fuzzybreaks = breaks + fuzz

            bins = pd.cut(x, bins=fuzzybreaks, labels=False,
                          right=right)
            width = np.diff(breaks)
            x = [breaks[i] + width[i] / 2
                 for i in range(len(breaks)-1)]
        else:
            # Proper scale trainning and mapping should never let
            # the code path get here. If there is a problem here,
            # something is probably wrong with the chosen scale
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

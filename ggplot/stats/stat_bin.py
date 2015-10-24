from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
import pandas as pd
import pandas.core.common as com
from six.moves import range, zip

from ..utils import seq, make_iterable_ntimes
from ..utils.exceptions import GgplotError, gg_warn
from ..scales.utils import fullseq
from .stat import stat


class stat_bin(stat):
    REQUIRED_AES = {'x'}
    DEFAULT_PARAMS = {'geom': 'histogram', 'position': 'stack',
                      'width': 0.9, 'drop': False, 'right': False,
                      'binwidth': None, 'bins': None,
                      'origin': None, 'breaks': None}
    DEFAULT_AES = {'y': '..count..', 'weight': None}
    CREATES = {'y', 'width'}

    def setup_params(self, data):
        params = self.params

        if 'y' in data or 'y' in params:
            msg = "stat_bin() must not be used with a y aesthetic."
            raise GgplotError(msg)

        if data['x'].dtype.kind == 'i':
            msg = ("stat_bin requires a continuous x variable the x "
                   "variable is discrete. "
                   "Perhaps you want stat='count'?")
            raise GgplotError(msg)

        if (params['breaks'] is None and
                params['binwidth'] is None and
                params['bins'] is None):
            msg = ("'stat_bin()' using 'bins = 30'. "
                   "Pick better value with 'binwidth'.")
            params = params.copy()
            params['bins'] = 30
            gg_warn(msg)

        return params

    @classmethod
    def compute_group(cls, data, scales, **params):
        params['range'] = np.asarray(scales.x.dimension())
        return bin(data['x'], data.get('weight'), **params)


def bin(x, weight, **params):
    x = np.asarray(x)
    breaks = params['breaks']
    right = params['right']
    origin = params['origin']
    rangee = params['range']
    binwidth = params['binwidth']
    num_bins = params['bins']

    if num_bins is None:
        num_bins = 30
    if binwidth is None:
        binwidth = np.ptp(rangee) / num_bins

    if x.dtype == np.int:
        bins = x
        x = np.unique(x)
        width = make_iterable_ntimes(params['width'], len(x))
    elif np.diff(rangee) == 0:
        bins = x
        width = make_iterable_ntimes(params['width'], len(x))
    elif com.is_numeric_dtype(x):
        if breaks is None:
            if origin is None:
                breaks = fullseq(rangee, binwidth, pad=True)
            else:
                breaks = seq(origin, np.max(rangee)+binwidth,
                             binwidth)

        fuzzybreaks = adjust_breaks(breaks, right)
        bins = pd.cut(x, bins=fuzzybreaks, labels=False,
                      right=right)
        width = np.diff(breaks)
        x = [b+w/2 for (b, w) in zip(breaks[:-1], width)]
    else:
        # Proper scale trainning and mapping should never let
        # the code path get here. If there is a problem here,
        # something is probably wrong with the chosen scale
        raise GgplotError("Cannot recognise the type of x")

    # If weight not supplied to, use one (no weight)
    if weight is None:
        weight = np.ones(len(bins))
    else:
        weight = np.asarray(
            make_iterable_ntimes(weight, len(bins)))
        weight[np.isnan(weight)] = 0

    # Create a dataframe with two columns:
    #   - the bins to which each x is assigned
    #   - the weight of each x value
    # Then create a weighted frequency table
    df = pd.DataFrame({'bins': bins,
                       'weight': weight})
    wftable = pd.pivot_table(df, values='weight',
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
            wftable.loc[b] = 0
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


def adjust_breaks(breaks, right):
    # fuzzy breaks to protect from floating point rounding errors
    diddle = 1e-07 * np.median(np.diff(breaks))
    if right:
        fuzz = np.hstack(
            [-diddle, np.repeat(diddle, len(breaks)-1)])
    else:
        fuzz = np.hstack(
            [np.repeat(-diddle, len(breaks)-1), diddle])

    fuzzybreaks = breaks + fuzz
    return fuzzybreaks

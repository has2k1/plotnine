from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
import pandas as pd
import pandas.core.common as com
from six.moves import range

from ..utils import seq, make_iterable_ntimes
from ..utils.exceptions import GgplotError, gg_warning
from ..scales.utils import fullseq
from .stat import stat


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

    @classmethod
    def _calculate(cls, data, scales, **params):
        if 'y' in data:
            raise GgplotError(_MSG_YVALUE)
        params['range'] = np.asarray(scales.x.dimension((0, 0)))
        params['weight'] = data.get('weight')
        return bin(data['x'], **params)


def bin(x, **params):
    x = np.asarray(x)
    breaks = params['breaks']
    right = params['right']
    binwidth = params['binwidth']
    origin = params['origin']
    rangee = params['range']
    weight = params.get('weight')

    if x.dtype == np.int:
        bins = x
        x = np.unique(x)
        width = make_iterable_ntimes(params['width'], len(x))
    elif np.diff(rangee) == 0:
        bins = x
        width = make_iterable_ntimes(params['width'], len(x))
    elif com.is_numeric_dtype(x):
        if breaks is None and binwidth is None:
            binwidth = np.ptp(rangee) / 30
            gg_warning(_MSG_BINWIDTH)
        if breaks is None:
            if origin is None:
                breaks = fullseq(rangee, binwidth, pad=True)
            else:
                breaks = seq(origin,
                             np.max(rangee)+binwidth,
                             binwidth)

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

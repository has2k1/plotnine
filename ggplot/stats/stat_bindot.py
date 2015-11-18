from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
import pandas as pd

from ..utils import groupby_apply
from ..utils.exceptions import GgplotError, gg_warn
from ..scales.utils import freedman_diaconis_bins
from .stat_bin import bin
from .stat import stat


class stat_bindot(stat):
    REQUIRED_AES = {'x'}
    DEFAULT_PARAMS = {'geom': 'dotplot', 'position': 'identity',
                      'bins': None, 'binwidth': None, 'origin': None,
                      'width': 0.9, 'binaxis': 'x',
                      'method': 'dotdensity', 'binpositions': 'bygroup',
                      'drop': False, 'right': True, 'na_rm': False,
                      'breaks': None}
    DEFAULT_AES = {'y': '..count..'}
    CREATES = {'y', 'width'}

    def setup_params(self, data):
        params = self.params

        if (params['breaks'] is None and
                params['binwidth'] is None and
                params['bins'] is None):
            params = params.copy()
            params['bins'] = freedman_diaconis_bins(data['x'])
            msg = ("'stat_bin()' using 'bins = {}'. "
                   "Pick better value with 'binwidth'.")
            gg_warn(msg.format(params['bins']))

        return params

    @classmethod
    def compute_panel(cls, data, scales, **params):
        if (params['method'] == 'dotdensity' and
                params['binpositions'] == 'all'):
            if params['binaxis'] == 'x':
                newdata = densitybin(x=data['x'],
                                     weight=data.get('weight'),
                                     binwidth=params['binwidth'],
                                     bins=params['bins'])
                data = data.sort_values('x')
                data.reset_index(inplace=True, drop=True)
                newdata = newdata.sort_values('x')
                newdata.reset_index(inplace=True, drop=True)
            elif params['binaxis'] == 'y':
                newdata = densitybin(x=data['y'],
                                     weight=data.get('weight'),
                                     binwidth=params['binwidth'],
                                     bins=params['bins'])
                data = data.sort_values('y')
                data.reset_index(inplace=True, drop=True)
                newdata = newdata.sort_values('x')
                newdata.reset_index(inplace=True, drop=True)

            data['bin'] = newdata['bin']
            data['binwidth'] = newdata['binwidth']
            data['weight'] = newdata['weight']
            data['bincenter'] = newdata['bincenter']
        return super(cls, stat_bindot).compute_panel(data, scales,
                                                     **params)

    @classmethod
    def compute_group(cls, data, scales, **params):
        # Check that weights are whole numbers
        # (for dots, weights must be whole)
        weight = data.get('weight')
        if weight is not None:
            int_status = [(w*1.0).is_integer() for w in weight]
            if not all(int_status):
                raise GgplotError(
                    "Weights for stat_bindot must be nonnegative integers.")

        if params['binaxis'] == 'x':
            rangee = scales.x.dimension((0, 0))
            values = data['x'].values
        elif params['binaxis'] == 'y':
            rangee = scales.y.dimension((0, 0))
            values = data['y'].values
            # The middle of each group, on the stack axis
            midline = np.mean([data['x'].min(), data['x'].max()])

        values_are_ints = values.dtype == np.dtype('int')
        if (params['breaks'] is None and
                params['binwidth'] is None and
                not values_are_ints):
            params['binwidth'] = np.ptp(rangee) / params['bins']

        if params['method'] == 'histodot':
            params['range'] = rangee
            params['weight'] = weight
            data = bin(values, **params)
            # for consistency
            data.rename(columns={'width': 'binwidth',
                                 'x': 'bincenter'},
                        inplace=True)
        elif params['method'] == 'dotdensity':
            # If bin centers are found by group instead of by all,
            # find the bin centers (If binpositions=="all", then
            # we'll already have bin centers.)
            if params['binpositions'] == 'bygroup':
                data = densitybin(x=values,
                                  weight=weight,
                                  binwidth=params['binwidth'],
                                  bins=params['bins'],
                                  rangee=rangee)

            # Collapse each bin and get a count
            def func(df):
                return pd.DataFrame({
                    'binwidth': [df['binwidth'].iloc[0]],
                    'bincenter': [df['bincenter'].iloc[0]],
                    'count': [int(df['weight'].sum())]})

            # plyr::ddply + plyr::summarize
            data = groupby_apply(data, 'bincenter', func)

            if data['count'].sum() != 0:
                data.loc[np.isnan(data['count']), 'count'] = 0
                data['ncount'] = data['count']/(data['count']
                                                .abs()
                                                .max())
                if params['drop']:
                    data = data[data['count'] > 0]
                    data.reset_index(inplace=True, drop=True)
                    data.is_copy = None

        if params['binaxis'] == 'x':
            data['x'] = data.pop('bincenter')
            # For x binning, the width of the geoms
            # is same as the width of the bin
            data['width'] = data['binwidth']
        elif params['binaxis'] == 'y':
            data['y'] = data.pop('bincenter')
            # For y binning, set the x midline.
            # This is needed for continuous x axis
            data['x'] = midline
        return data


def densitybin(x, weight=None, binwidth=None, bins=None, rangee=None):
    """
    Do density binning

    It does not collapse each bin with a count.

    Parameters
    ----------
    x : array-like
        Numbers to bin
    weight : array-like
        Weights
    binwidth : numeric
        Size of the bins
    rangee : tuple
        Range of x

    Returns
    -------
    data : DataFrame
    """
    if all(pd.isnull(x)):
        return pd.DataFrame()

    if weight is None:
        weight = np.ones(len(x))
    weight = np.asarray(weight)
    weight[np.isnan(weight)] = 0

    if rangee is None:
        rangee = np.min(x), np.max(x)
    if bins is None:
        bins = 30
    if binwidth is None:
        binwidth = np.ptp(rangee) / bins

    # Sort weight and x, by x
    order = np.argsort(x)
    weight = weight[order]
    x = x[order]

    cbin = 0                # Current bin ID
    binn = [None] * len(x)  # The bin ID for each observation
    # End position of current bin (scan left to right)
    binend = -np.inf

    # Scan list and put dots in bins
    for i, value in enumerate(x):
        # If past end of bin, start a new bin at this point
        if value >= binend:
            binend = value + binwidth
            cbin = cbin + 1
        binn[i] = cbin

    def func(series):
        return (series.min()+series.max())/2

    results = pd.DataFrame({'x': x,
                            'bin': binn,
                            'binwidth': binwidth,
                            'weight': weight})
    # This is a plyr::ddply
    results['bincenter'] = results.groupby('bin')['x'].transform(func)
    return results

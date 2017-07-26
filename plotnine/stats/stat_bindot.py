from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from warnings import warn

import numpy as np
import pandas as pd

from ..utils import groupby_apply
from ..doctools import document
from ..exceptions import PlotnineError
from .binning import (breaks_from_bins, breaks_from_binwidth,
                      assign_bins, freedman_diaconis_bins)
from .stat import stat


@document
class stat_bindot(stat):
    """
    Binning for a dot plot

    {usage}

    Parameters
    ----------
    {common_parameters}
    bins : int, optional (default: None)
        Number of bins. Overridden by binwidth. If :py:`None`,
        a number is computed using the freedman-diaconis method.
    binwidth : float, optional (default: None)
        When :py:`method='dotdensity'`, this specifies the maximum
        binwidth. When :py:`method='histodot'`, this specifies the
        binwidth. This supercedes the ``bins``.
    origin : float, optional (default: None)
        When :py:`method='histodot'`, origin of the first bin.
    width : float, optional (default: 0.9)
        When :py:`binaxis='y'`, the spacing of the dotstacks for
        dodging.
    binaxis : str, optional (default: x)
        Axis to bin along. Either :py:`'x'` or :py:`'y'`
    method : str, optional (default: dotdensity)
        One of *dotdensity* or *histodot*. These provide either of
        dot-density binning or fixed bin widths.
    binpositions : str, optional (default: bygroup)
        Position of the bins when :py:`method='dotdensity'`. The value
        is one of::

            'bygroup'  # positions of the bins for each group are
                       # determined separately.
            'all'      # positions of the bins are determined with all
                       # data taken together. This aligns the dots
                       # stacks across multiple groups.

    drop : bool, optional (default: False)
        If :py:`True`, remove all bins with zero counts.
    right : bool, optional (default: True)
        When :py:`method='histodot'`, :py:`True` means include right
        edge of the bins and if :py:`False` the left edge is included.
    breaks : array-like, optional (default: None)
        Bin boundaries for :py:`method='histodot'`. This supercedes the
        ``binwidth`` and ``bins``.

    {aesthetics}

    .. rubric:: Options for computed aesthetics

    ::

         '..count..'    # number of points in bin
         '..density..'  # density of points in bin, scaled to integrate to 1
         '..ncount..'   # count, scaled to maximum of 1
         '..ndensity..' # density, scaled to maximum of 1

    See Also
    --------
    :class:`~plotnine.stats.stat_bin`
    """
    REQUIRED_AES = {'x'}
    DEFAULT_PARAMS = {'geom': 'dotplot', 'position': 'identity',
                      'na_rm': False,
                      'bins': None, 'binwidth': None, 'origin': None,
                      'width': 0.9, 'binaxis': 'x',
                      'method': 'dotdensity', 'binpositions': 'bygroup',
                      'drop': False, 'right': True, 'na_rm': False,
                      'breaks': None}
    DEFAULT_AES = {'y': '..count..'}
    CREATES = {'width', 'count', 'density', 'ncount', 'ndensity'}

    def setup_params(self, data):
        params = self.params

        if (params['breaks'] is None and
                params['binwidth'] is None and
                params['bins'] is None):
            params = params.copy()
            params['bins'] = freedman_diaconis_bins(data['x'])
            msg = ("'stat_bin()' using 'bins = {}'. "
                   "Pick better value with 'binwidth'.")
            warn(msg.format(params['bins']))

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
                raise PlotnineError(
                    "Weights for stat_bindot must be nonnegative integers.")

        if params['binaxis'] == 'x':
            rangee = scales.x.dimension((0, 0))
            values = data['x'].values
        elif params['binaxis'] == 'y':
            rangee = scales.y.dimension((0, 0))
            values = data['y'].values
            # The middle of each group, on the stack axis
            midline = np.mean([data['x'].min(), data['x'].max()])

        if params['method'] == 'histodot':
            if params['binwidth'] is not None:
                breaks = breaks_from_binwidth(
                    rangee, params['binwidth'], boundary=params['origin'])
            else:
                breaks = breaks_from_bins(
                    rangee, params['bins'], boundary=params['origin'])

            closed = 'right' if params['right'] else 'left'
            data = assign_bins(
                values, breaks, data.get('weight'),
                pad=False, closed=closed)
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

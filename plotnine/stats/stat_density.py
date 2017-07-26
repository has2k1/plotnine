from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import numpy as np
import pandas as pd
import statsmodels.api as sm
import six

from ..doctools import document
from ..exceptions import PlotnineError
from ..utils import suppress
from .stat import stat


# NOTE: Parameter discriptions are in
# statsmodels/nonparametric/kde.py
@document
class stat_density(stat):
    """
    Compute density estimate

    {usage}

    Parameters
    ----------
    {common_parameters}
    kernel : str, optional (default: 'gaussian')
        Kernel used for density estimation. One of::

            'biweight'
            'cosine'
            'cosine2'
            'epanechnikov'
            'gaussian'
            'triangular'
            'triweight'
            'uniform'

    adjust : float, optional (default: 1)
        An adjustment factor for the ``bw``. Bandwidth becomes
        :py:`bw * adjust`.
        Adjustment of the bandwidth.
    trim : bool, optional (default: False)
        This parameter only matters if you are displaying multiple
        densities in one plot. If :py:`False`, the default, each
        density is computed on the full range of the data. If
        :py:`True`, each density is computed over the range of that
        group; this typically means the estimated x values will not
        line-up, and hence you won't be able to stack density values.
    n : int, optional(default: 1024)
        Number of equally spaced points at which the density is to
        be estimated. For efficient computation, it should be a power
        of two.
    gridsize : int, optional (default: None)
        If gridsize is :py:`None`, :py:`max(len(x), 50)` is used.
    bw : str or float, optional (default: 'normal_reference')
        The bandwidth to use, If a float is given, it is the bandwidth.
        The :py:`str` choices are::

            'normal_reference'
            'scott'
            'silverman'

    cut :, optional (default: 3)
        Defines the length of the grid past the lowest and highest
        values of ``x`` so that the kernel goes to zero. The end points
        are ``-/+ cut*bw*{min(x) or max(x)}``.
    clip : tuple, optional (default: (-np.inf, np.inf))
        Values in ``x`` that are outside of the range given by clip are
        dropped. The number of values in ``x`` is then shortened.

    {aesthetics}

    .. rubric:: Options for computed aesthetics

    ::

        '..density..'   # density estimate

        '..count..'     # density * number of points,
                        # useful for stacked density plots

        '..scaled..'    # density estimate, scaled to maximum of 1

    See Also
    --------
    * :class:`~plotnine.geoms.geom_density`
    * :class:`statsmodels.nonparametric.kde.KDEUnivariate`
    * :meth:`statsmodels.nonparametric.kde.KDEUnivariate.fit`
    """
    REQUIRED_AES = {'x'}
    DEFAULT_PARAMS = {'geom': 'density', 'position': 'stack',
                      'na_rm': False,
                      'kernel': 'gaussian', 'adjust': 1,
                      'trim': False, 'n': 1024, 'gridsize': None,
                      'bw': 'normal_reference', 'cut': 3,
                      'clip': (-np.inf, np.inf)}
    DEFAULT_AES = {'y': '..density..'}
    CREATES = {'density', 'count', 'scaled', 'n'}

    def setup_params(self, data):
        params = self.params.copy()
        lookup = {
            'biweight': 'biw',
            'cosine': 'cos',
            'cosine2': 'cos2',
            'epanechnikov': 'epa',
            'gaussian': 'gau',
            'triangular': 'tri',
            'triweight': 'triw',
            'uniform': 'uni'}

        with suppress(KeyError):
            params['kernel'] = lookup[params['kernel'].lower()]

        if params['kernel'] not in six.viewvalues(lookup):
            msg = ("kernel should be one of {}. "
                   "You may use the abbreviations {}")
            raise PlotnineError(msg.format(six.viewkeys(lookup),
                                           six.viewvalues(lookup)))

        return params

    @classmethod
    def compute_group(cls, data, scales, **params):
        weight = data.get('weight')

        if params['trim']:
            range_x = data['x'].min(), data['x'].max()
        else:
            range_x = scales.x.dimension()

        return compute_density(data['x'], weight, range_x, **params)


def compute_density(x, weight, range, **params):
    x = np.asarray(x, dtype=np.float)
    not_nan = ~np.isnan(x)
    x = x[not_nan]

    n = len(x)

    if weight is None:
        weight = np.ones(n) / n

    # if less than 3 points, spread density evenly
    # over points
    if n < 3:
        return pd.DataFrame({
            'x': x,
            'density': weight / np.sum(weight),
            'scaled': weight / np.max(weight),
            'count': 1,
            'n': n})

    # kde is computed efficiently using fft. But the fft does
    # not support weights and is only available with the
    # gaussian kernel. When weights are relevant we
    # turn off the fft.
    if params['kernel'] == 'gau':
        fft, weight = True, None
    else:
        fft = False

    kde = sm.nonparametric.KDEUnivariate(x)
    kde.fit(
        kernel=params['kernel'],
        bw=params['bw'],
        fft=fft,
        weights=weight,
        adjust=params['adjust'],
        cut=params['cut'],
        gridsize=params['gridsize'],
        clip=params['clip'])

    x2 = np.linspace(range[0], range[1], params['n'])

    try:
        y = kde.evaluate(x2)
    except ValueError:
        y = []
        for _x in x2:
            result = kde.evaluate(_x)
            try:
                y.append(result[0])
            except TypeError:
                y.append(result)

    y = np.asarray(y)

    # Evaluations outside the kernel domain return np.nan,
    # these values and corresponding x2s are dropped.
    # The kernel domain is defined by the values in x, but
    # the evaluated values in x2 could have a much wider range.
    not_nan = ~np.isnan(y)
    x2 = x2[not_nan]
    y = y[not_nan]
    return pd.DataFrame({'x': x2,
                         'density': y,
                         'scaled': y / np.max(y),
                         'count': y * n,
                         'n': n})

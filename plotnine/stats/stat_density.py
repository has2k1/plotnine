from contextlib import suppress
from warnings import warn

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import iqr

from ..doctools import document
from ..exceptions import PlotnineError, PlotnineWarning
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
    bw : str or float, optional (default: 'nrd0')
        The bandwidth to use, If a float is given, it is the bandwidth.
        The :py:`str` choices are::

            'nrd0'
            'normal_reference'
            'scott'
            'silverman'

        ``nrd0`` is a port of ``stats::bw.nrd0`` in R; it is eqiuvalent
        to ``silverman`` when there is more than 1 value in a group.
    cut : float, optional (default: 3)
        Defines the length of the grid past the lowest and highest
        values of ``x`` so that the kernel goes to zero. The end points
        are ``-/+ cut*bw*{min(x) or max(x)}``.
    clip : tuple, optional (default: (-np.inf, np.inf))
        Values in ``x`` that are outside of the range given by clip are
        dropped. The number of values in ``x`` is then shortened.

    See Also
    --------
    plotnine.geoms.geom_density
    statsmodels.nonparametric.kde.KDEUnivariate
    statsmodels.nonparametric.kde.KDEUnivariate.fit
    """

    _aesthetics_doc = """
    {aesthetics_table}

    .. rubric:: Options for computed aesthetics

    ::

        'density'   # density estimate

        'count'     # density * number of points,
                    # useful for stacked density plots

        'scaled'    # density estimate, scaled to maximum of 1

    """
    REQUIRED_AES = {'x'}
    DEFAULT_PARAMS = {'geom': 'density', 'position': 'stack',
                      'na_rm': False,
                      'kernel': 'gaussian', 'adjust': 1,
                      'trim': False, 'n': 1024, 'gridsize': None,
                      'bw': 'nrd0', 'cut': 3,
                      'clip': (-np.inf, np.inf)}
    DEFAULT_AES = {'y': 'stat(density)'}
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

        if params['kernel'] not in lookup.values():
            msg = ("kernel should be one of {}. "
                   "You may use the abbreviations {}")
            raise PlotnineError(msg.format(lookup.keys(),
                                           lookup.values()))

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
    bw = params['bw']
    n = len(x)

    if n == 0 or (n == 1 and isinstance(bw, str)):
        if n == 1:
            warn("To compute the density of a group with only one "
                 "value set the bandwidth manually. e.g `bw=0.1`",
                 PlotnineWarning)
        warn("Groups with fewer than 2 data points have been removed.",
             PlotnineWarning)
        return pd.DataFrame()

    if weight is None:
        weight = np.ones(n) / n
    else:
        weight = np.asarray(weight, dtype=float)

    # kde is computed efficiently using fft. But the fft does
    # not support weights and is only available with the
    # gaussian kernel. When weights are relevant we
    # turn off the fft.
    if params['kernel'] == 'gau' and weight is None:
        fft = True
    else:
        fft = False

    if bw == 'nrd0':
        bw = nrd0(x)
    kde = sm.nonparametric.KDEUnivariate(x)
    kde.fit(
        kernel=params['kernel'],
        bw=bw,
        fft=fft,
        weights=weight,
        adjust=params['adjust'],
        cut=params['cut'],
        gridsize=params['gridsize'],
        clip=params['clip'])

    x2 = np.linspace(range[0], range[1], params['n'])

    try:
        y = kde.evaluate(x2)
        if np.isscalar(y) and np.isnan(y):
            raise ValueError('kde.evaluate returned nan')
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
                         'scaled': y / np.max(y) if len(y) else [],
                         'count': y * n,
                         'n': n})


def nrd0(x):
    """
    Port of R stats::bw.nrd0

    This is equivalent to statsmodels silverman when x has more than
    1 unique value. It can never give a zero bandwidth.

    Parameters
    ----------
    x : array_like
        Values whose density is to be estimated

    Returns
    -------
    out : float
        Bandwidth of x
    """
    n = len(x)
    if n < 1:
        raise ValueError(
            "Need at leat 2 data points to compute the nrd0 bandwidth."
        )

    std = np.std(x, ddof=1)
    std_estimate = iqr(x)/1.349
    low_std = np.min((std, std_estimate))
    if low_std == 0:
        low_std = std_estimate or np.abs(np.asarray(x)[0]) or 1
    return 0.9 * low_std * (n ** -0.2)

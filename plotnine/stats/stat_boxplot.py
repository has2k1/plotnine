import numpy as np
import pandas as pd
import pandas.api.types as pdtypes

from ..utils import resolution
from ..doctools import document
from .stat import stat


@document
class stat_boxplot(stat):
    """
    Compute boxplot statistics

    {usage}

    Parameters
    ----------
    {common_parameters}
    coef : float, optional (default: 1.5)
        Length of the whiskers as a multiple of the Interquartile
        Range.

    See Also
    --------
    plotnine.geoms.geom_boxplot
    """

    _aesthetics_doc = """
    {aesthetics_table}

    .. rubric:: Options for computed aesthetics

    ::

        'width'  # width of boxplot
        'lower'  # lower hinge, 25% quantile
        'middle' # median, 50% quantile
        'upper'  # upper hinge, 75% quantile

        'notchlower' #  lower edge of notch, computed as;
                     # median - 1.58 * IQR / sqrt(n)

        'notchupper' # upper edge of notch, computed as;
                     # median + 1.58 * IQR / sqrt(n)

        'ymin'  # lower whisker, computed as; smallest observation
                # greater than or equal to lower hinge - 1.5 * IQR

        'ymax'  # upper whisker, computed as; largest observation
                # less than or equal to upper hinge + 1.5 * IQR

    Calculated aesthetics are accessed using the `after_stat` function.
    e.g. :py:`after_stat('width')`.
    """

    REQUIRED_AES = {'x', 'y'}
    NON_MISSING_AES = {'weight'}
    DEFAULT_PARAMS = {'geom': 'boxplot', 'position': 'dodge',
                      'na_rm': False, 'coef': 1.5, 'width': None}
    CREATES = {'lower', 'upper', 'middle', 'ymin', 'ymax',
               'outliers', 'notchupper', 'notchlower', 'width',
               'relvarwidth'}

    def setup_params(self, data):
        if self.params['width'] is None:
            self.params['width'] = resolution(data['x'], False) * 0.75
        return self.params

    @classmethod
    def compute_group(cls, data, scales, **params):
        y = data['y'].to_numpy()
        weights = data.get('weight', None)
        total_weight = len(y) if weights is None else np.sum(weights)
        res = weighted_boxplot_stats(y, weights=weights, whis=params['coef'])

        if len(np.unique(data['x'])) > 1:
            width = np.ptp(data['x']) * 0.9
        else:
            width = params['width']

        if pdtypes.is_categorical_dtype(data['x']):
            x = data['x'].iloc[0]
        else:
            x = np.mean([data['x'].min(), data['x'].max()])

        d = {
            'ymin': res['whislo'],
            'lower': res['q1'],
            'middle': [res['med']],
            'upper': res['q3'],
            'ymax': res['whishi'],
            'outliers': [res['fliers']],
            'notchupper': res['cihi'],
            'notchlower': res['cilo'],
            'x': x,
            'width': width,
            'relvarwidth': np.sqrt(total_weight)
        }
        return pd.DataFrame(d)


def weighted_percentile(a, q, weights=None):
    """
    Compute the weighted q-th percentile of data

    Parameters
    ----------
    a : array_like
        Input that can be converted into an array.
    q : array_like[float]
        Percentile or sequence of percentiles to compute. Must be int
        the range [0, 100]
    weights : array_like
        Weights associated with the input values.
    """
    # Calculate and interpolate weighted percentiles
    # method derived from https://en.wikipedia.org/wiki/Percentile
    # using numpy's standard C = 1
    if weights is None:
        weights = np.ones(len(a))

    weights = np.asarray(weights)
    q = np.asarray(q)

    C = 1
    idx_s = np.argsort(a)
    a_s = a[idx_s]
    w_n = weights[idx_s]
    S_N = np.sum(weights)
    S_n = np.cumsum(w_n)
    p_n = (S_n - C * w_n) / (S_N + (1 - 2 * C) * w_n)
    pcts = np.interp(q / 100.0, p_n, a_s)
    return pcts


def weighted_boxplot_stats(x, weights=None, whis=1.5):
    """
    Calculate weighted boxplot plot statistics

    Parameters
    ----------
    x : array_like
        Data
    weights : array_like, optional
        Weights associated with the data.
    whis : float, optional (default: 1.5)
        Position of the whiskers beyond the interquartile range.
        The data beyond the whisker are considered outliers.

        If a float, the lower whisker is at the lowest datum above
        ``Q1 - whis*(Q3-Q1)``, and the upper whisker at the highest
        datum below ``Q3 + whis*(Q3-Q1)``, where Q1 and Q3 are the
        first and third quartiles.  The default value of
        ``whis = 1.5`` corresponds to Tukey's original definition of
        boxplots.

    Notes
    -----
    This method adapted from Matplotlibs boxplot_stats. The key difference
    is the use of a weighted percentile calculation and then using linear
    interpolation to map weight percentiles back to data.
    """
    if weights is None:
        q1, med, q3 = np.percentile(x, (25, 50, 75))
        n = len(x)
    else:
        q1, med, q3 = weighted_percentile(x, (25, 50, 75), weights)
        n = np.sum(weights)

    iqr = q3 - q1
    mean = np.average(x, weights=weights)
    cilo = med - 1.58 * iqr / np.sqrt(n)
    cihi = med + 1.58 * iqr / np.sqrt(n)

    # low extreme
    loval = q1 - whis * iqr
    lox = x[x >= loval]
    if len(lox) == 0 or np.min(lox) > q1:
        whislo = q1
    else:
        whislo = np.min(lox)

    # high extreme
    hival = q3 + whis * iqr
    hix = x[x <= hival]
    if len(hix) == 0 or np.max(hix) < q3:
        whishi = q3
    else:
        whishi = np.max(hix)

    bpstats = {
        'fliers': x[(x < whislo) | (x > whishi)],
        'mean': mean,
        'med': med,
        'q1': q1,
        'q3': q3,
        'iqr': iqr,
        'whislo': whislo,
        'whishi': whishi,
        'cilo': cilo,
        'cihi': cihi,
    }
    return bpstats

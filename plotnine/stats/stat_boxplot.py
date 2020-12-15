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
                     # :py:`median - 1.58 * IQR / sqrt(n)`

        'notchupper' # upper edge of notch, computed as;
                     # :py:`median + 1.58 * IQR / sqrt(n)`

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
        try:
            weights = np.array(data['weight'])
        except KeyError:
            weights = np.ones(len(data['y']))
        y = np.array(data['y'])
        res = weighted_boxplot_stats(y, weights=weights, whis=params['coef'])

        if len(np.unique(data['x'])) > 1:
            width = np.ptp(data['x']) * 0.9
        else:
            width = params['width']

        if pdtypes.is_categorical_dtype(data['x']):
            x = data['x'].iloc[0]
        else:
            x = np.mean([data['x'].min(), data['x'].max()])

        d = {'ymin': res['whislo'],
             'lower': res['q1'],
             'middle': [res['med']],
             'upper': res['q3'],
             'ymax': res['whishi'],
             'outliers': [res['fliers']],
             'notchupper': res['cihi'],
             'notchlower': res['cilo'],
             'x': x,
             'width': width,
             'relvarwidth': np.sqrt(np.sum(weights))}
        return pd.DataFrame(d)


def weighted_percentile(X, weights, percentile):
    # Calculate and interpolate weighted percentiles
    # method derived from https://en.wikipedia.org/wiki/Percentile
    # using numpy's standard C = 1
    C = 1
    idx_s = np.argsort(X)
    X_s = X[idx_s]
    w_n = weights[idx_s]
    S_N = np.sum(weights)
    S_n = np.cumsum(w_n)
    p_n = (S_n - C * w_n) / (S_N + (1 - 2 * C) * w_n)
    pcts = np.interp(np.array(percentile) / 100.0, p_n, X_s)
    return pcts


def weighted_boxplot_stats(x, weights, whis=1.5):
    # Weighted boxplot stats is adapted from MPL's boxplot_stats
    # with the use of a weighted interpolated percentile calculation
    q1, med, q3 = weighted_percentile(x, weights, [25, 50, 75])
    iqr = q3 - q1
    mean = np.average(x, weights=weights)
    n = np.sum(weights)
    cilo = med - 1.58 * iqr / np.sqrt(n)
    cihi = med + 1.58 * iqr / np.sqrt(n)

    loval = q1 - whis * iqr
    lox = x[x >= loval]
    if len(lox) == 0 or np.min(lox) > q1:
        whislo = q1
    else:
        whislo = np.min(lox)

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

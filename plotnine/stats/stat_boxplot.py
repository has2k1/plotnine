import numpy as np
import pandas as pd
import pandas.api.types as pdtypes
from matplotlib.cbook import boxplot_stats
from warnings import warn

from ..exceptions import PlotnineWarning
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
        labels = ['x', 'y']
        try:
            weight_type = data['weight'].dtype
            if weight_type.kind != 'u':
                warn(
                    "Weight is not an unsigned integer type and "
                    "will be coerced.",
                    PlotnineWarning
                    )
            indices = data.index.repeat(data['weight'])
            X = np.array(data[labels].loc[indices])
        except KeyError:
            X = np.array(data[labels])
        res = boxplot_stats(X, whis=params['coef'], labels=labels)[1]
        try:
            n = data['weight'].sum()
        except KeyError:
            n = len(data['y'])

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
             'notchupper': res['med']+1.58*res['iqr']/np.sqrt(n),
             'notchlower': res['med']-1.58*res['iqr']/np.sqrt(n),
             'x': x,
             'width': width,
             'relvarwidth': np.sqrt(n)}
        return pd.DataFrame(d)

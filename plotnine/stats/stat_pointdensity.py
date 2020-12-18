import numpy as np
import pandas as pd

from ..mapping.evaluation import after_stat
from ..doctools import document
from .stat import stat
from .density import kde, get_var_type


@document
class stat_pointdensity(stat):
    """
    Compute density estimation for each point

    {usage}

    Parameters
    ----------
    {common_parameters}
    package : str in ``['statsmodels', 'scipy', 'sklearn']``
        Package whose kernel density estimation to use. Default is
        statsmodels.
    kde_params : dict
        Keyword arguments to pass on to the kde class.

    See Also
    --------
    statsmodels.nonparametric.kde.KDEMultivariate
    scipy.stats.gaussian_kde
    sklearn.neighbors.KernelDensity
    """

    _aesthetics_doc = """
    {aesthetics_table}

    .. rubric:: Options for computed aesthetics

    ::

        'density'   # Computed density at a point

    """
    REQUIRED_AES = {'x', 'y'}
    DEFAULT_AES = {'color': after_stat('density')}
    DEFAULT_PARAMS = {'geom': 'density_2d', 'position': 'identity',
                      'na_rm': False, 'package': 'statsmodels',
                      'kde_params': None}
    CREATES = {'density'}

    def setup_params(self, data):
        params = self.params.copy()
        if params['kde_params'] is None:
            params['kde_params'] = dict()

        kde_params = params['kde_params']
        if params['package'] == 'statsmodels':
            params['package'] = 'statsmodels-m'
            if 'var_type' not in kde_params:
                kde_params['var_type'] = '{}{}'.format(
                    get_var_type(data['x']),
                    get_var_type(data['y'])
                )

        return params

    @classmethod
    def compute_group(cls, data, scales, **params):
        package = params['package']
        kde_params = params['kde_params']

        var_data = np.array([data['x'].values, data['y'].values]).T
        density = kde(var_data, var_data, package, **kde_params)

        data = pd.DataFrame({
            'x': data['x'],
            'y': data['y'],
            'density': density.flatten(),
        })

        return data

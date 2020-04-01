import numpy as np
import pandas as pd
from scipy.stats.mstats import plotting_positions

from ..doctools import document
from ..exceptions import PlotnineError
from .distributions import get_continuous_distribution
from .stat import stat


# Note: distribution should be a name from scipy.stat.distribution
@document
class stat_qq(stat):
    """
    Calculation for quantile-quantile plot

    {usage}

    Parameters
    ----------
    {common_parameters}
    distribution : str (default: norm)
        Distribution or distribution function name. The default is
        *norm* for a normal probability plot. Objects that look enough
        like a stats.distributions instance (i.e. they have a ppf
        method) are also accepted. See :mod:`scipy stats <scipy.stats>`
        for available distributions.
    dparams : dict
        Distribution-specific shape parameters (shape parameters plus
        location and scale).
    quantiles : array_like, optional
        Probability points at which to calculate the theoretical
        quantile values. If provided, must be the same number as
        as the sample data points. The default is to use calculated
        theoretical points, use to ``alpha_beta`` control how
        these points are generated.
    alpha_beta : tuple
        Parameter values to use when calculating the quantiles.
        Default is :py:`(3/8, 3/8)`.

    See Also
    --------
    scipy.stats.mstats.plotting_positions : Uses ``alpha_beta``
        to calculate the quantiles.
    """

    _aesthetics_doc = """
    {aesthetics_table}

    .. rubric:: Options for computed aesthetics

    ::

         'theoretical'  # theoretical quantiles
         'sample'       # sample quantiles

    """
    REQUIRED_AES = {'sample'}
    DEFAULT_AES = {'x': 'stat(theoretical)', 'y': 'stat(sample)'}
    DEFAULT_PARAMS = {'geom': 'qq', 'position': 'identity',
                      'na_rm': False,
                      'distribution': 'norm', 'dparams': (),
                      'quantiles': None, 'alpha_beta': (3/8, 3/8)}

    @classmethod
    def compute_group(cls, data, scales, **params):
        sample = data['sample'].sort_values().values
        alpha, beta = params['alpha_beta']
        quantiles = params['quantiles']

        if quantiles is None:
            quantiles = plotting_positions(sample, alpha, beta)
        elif len(quantiles) != len(sample):
            raise PlotnineError(
                "The number of quantile values is not the same as "
                "the number of sample values.")

        quantiles = np.asarray(quantiles)
        cdist = get_continuous_distribution(params['distribution'])
        theoretical = cdist.ppf(quantiles, *params['dparams'])
        return pd.DataFrame({'sample': sample,
                             'theoretical': theoretical})

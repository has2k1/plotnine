from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pandas as pd
from scipy.stats import probplot

from ..doctools import document
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

    {aesthetics}

    .. rubric:: Options for computed aesthetics

    ::

         '..theoretical..'  # theoretical quantiles
         '..sample..'       # sample quantiles

    See Also
    --------
    :func:`scipy.stats.probplot` calculates the quantiles.
    """
    REQUIRED_AES = {'sample'}
    DEFAULT_AES = {'x': '..theoretical..', 'y': '..sample..'}
    DEFAULT_PARAMS = {'geom': 'qq', 'position': 'identity',
                      'na_rm': False,
                      'distribution': 'norm', 'dparams': ()}

    @classmethod
    def compute_group(cls, data, scales, **params):
        theoretical, sample = probplot(data['sample'],
                                       dist=params['distribution'],
                                       sparams=params['dparams'],
                                       fit=False)
        return pd.DataFrame({'sample': sample,
                             'theoretical': theoretical})

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pandas as pd
from scipy.stats import probplot

from ..utils.doctools import document
from .stat import stat


# Note: distribution should be a name from scipy.stat.distribution
@document
class stat_qq(stat):
    """
    Calculation for quantile-quantile plot

    {documentation}

    .. rubric:: Options for computed aesthetics

    x
        - ``..theoretical..`` - theoretical quantiles

    y
        - ``..sample..`` - sample quantiles
    """
    REQUIRED_AES = {'sample'}
    DEFAULT_AES = {'x': '..theoretical..', 'y': '..sample..'}
    DEFAULT_PARAMS = {'geom': 'qq', 'position': 'identity',
                      'distribution': 'norm', 'dparams': ()}

    @classmethod
    def compute_group(cls, data, scales, **params):
        theoretical, sample = probplot(data['sample'],
                                       dist=params['distribution'],
                                       sparams=params['dparams'],
                                       fit=False)
        return pd.DataFrame({'sample': sample,
                             'theoretical': theoretical})

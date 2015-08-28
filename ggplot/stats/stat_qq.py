from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pandas as pd
from scipy.stats import probplot

from .stat import stat


# Note: distribution should be a name from scipy.stat.distribution
class stat_qq(stat):
    REQUIRED_AES = {'sample'}
    DEFAULT_AES = {'x': '..theoretical..', 'y': '..sample..'}
    DEFAULT_PARAMS = {'geom': 'point', 'position': 'identity',
                      'distribution': 'norm', 'dparams': ()}

    @classmethod
    def _calculate(cls, data, scales, **params):
        theoretical, sample = probplot(data['sample'],
                                       dist=params['distribution'],
                                       sparams=params['dparams'],
                                       fit=False)
        return pd.DataFrame({'sample': sample,
                             'theoretical': theoretical})

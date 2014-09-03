from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde

from ..utils.exceptions import GgplotError
from .stat import stat


# TODO: switch to statsmodels kdes
class stat_density(stat):
    REQUIRED_AES = {'x'}
    DEFAULT_PARAMS = {'geom': 'density', 'position': 'stack',
                      'kernel': 'gaussian', 'adjust': 1, 'trim': False}

    CREATES = {'y'}

    def _calculate(self, data, scales, **kwargs):
        x = data.pop('x')
        range_x = scales.x.dimension((0, 0))  # TODO: Use this

        try:
            float(x.iloc[0])
        except:
            try:
                # try to use it as a pandas.tslib.Timestamp
                x = [ts.toordinal() for ts in x]
            except:
                raise GgplotError(
                    "stat_density(): aesthetic x mapping " +
                    "needs to be convertable to float!")
        # TODO: Implement weight
        try:
            weight = data.pop('weight')
        except KeyError:
            weight = np.ones(len(x))

        kde = gaussian_kde(x)
        x2 = np.linspace(range_x[0], range_x[1], 1000)
        y = kde.evaluate(x2)
        new_data = pd.DataFrame({'x': x2, 'y': y})
        return new_data

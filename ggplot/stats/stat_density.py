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

        # TODO: Get "full" range of densities
        # i.e tail off to zero like ggplot2? But there is nothing
        # wrong with the current state.
        kde = gaussian_kde(x)
        bottom = np.min(x)
        top = np.max(x)
        step = (top - bottom) / 1000.0

        x = np.arange(bottom, top, step)
        y = kde.evaluate(x)
        new_data = pd.DataFrame({'x': x, 'y': y})
        return new_data

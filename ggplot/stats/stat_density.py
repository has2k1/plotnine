from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from .stat import stat
from scipy.stats import gaussian_kde
import numpy as np


class stat_density(stat):
    REQUIRED_AES = {'x'}
    DEFAULT_PARAMS = {'geom': 'density', 'position': 'stack',
                      'kernel': 'gaussian', 'adjust': 1, 'trim': False}

    CREATES = {'y'}

    def _calculate(self, pinfo):
        x = pinfo['x']

        try:
            float(x[0])
        except:
            try:
                # try to use it as a pandas.tslib.Timestamp
                x = [ts.toordinal() for ts in x]
            except:
                raise Exception("stat_density(): aesthetic x mapping " +
                                "needs to be convertable to float!")
        # TODO: Implement weight
        # weight = pinfo.pop('weight')

        # TODO: Get "full" range of densities
        # i.e tail off to zero like ggplot2? But there is nothing
        # wrong with the current state.
        kde = gaussian_kde(x)
        bottom = np.min(x)
        top = np.max(x)
        step = (top - bottom) / 1000.0
        x = np.arange(bottom, top, step)
        pinfo['x'] = x
        pinfo['y'] = kde.evaluate(x)
        return pinfo

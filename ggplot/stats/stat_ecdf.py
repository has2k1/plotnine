from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
import pandas as pd
from statsmodels.distributions.empirical_distribution import ECDF

from ..utils import seq
from .stat import stat


class stat_ecdf(stat):
    REQUIRED_AES = {'x'}
    DEFAULT_PARAMS = {'geom': 'step', 'position': 'identity',
                      'n': None}
    DEFAULT_AES = {'y': '..y..'}
    CREATES = {'y'}

    @classmethod
    def compute_group(cls, data, scales, **params):
        # If n is None, use raw values; otherwise interpolate
        if params['n'] is None:
            xvals = np.unique(data['x'])
        else:
            xvals = seq(data['x'].min(), data['x'].max(),
                        length_out=params['n'])

        y = ECDF(data['x'])(xvals)

        # make point with y = 0, from plot.stepfun
        rx = xvals.min(), xvals.max()
        if len(xvals) > 1:
            dr = np.max([.08*np.diff(rx)[0], np.median(np.diff(xvals))])
        else:
            dr = np.abs(xvals)/16

        x0 = rx[0] - dr
        x1 = rx[1] + dr
        y0 = 0
        y1 = 1

        res = pd.DataFrame({
            'x': np.hstack([x0, xvals, x1]),
            'y': np.hstack([y0, y, y1])})
        return res

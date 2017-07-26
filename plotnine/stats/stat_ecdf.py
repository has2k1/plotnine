from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
import pandas as pd
from statsmodels.distributions.empirical_distribution import ECDF

from ..doctools import document
from .stat import stat


@document
class stat_ecdf(stat):
    """
    Emperical Cumulative Density Function

    {usage}

    Parameters
    ----------
    {common_parameters}
    n  : int (default: None)
        This is the number of points to interpolate with.
        If :py:`None`, do not interpolate.

    {aesthetics}

    .. rubric:: Options for computed aesthetics

    ::

        '..x..'  # x in the data
        '..y..'  # cumulative density corresponding to x

    See Also
    --------
    :class:`~plotnine.geoms.geom_step`
    """
    REQUIRED_AES = {'x'}
    DEFAULT_PARAMS = {'geom': 'step', 'position': 'identity',
                      'na_rm': False, 'n': None}
    DEFAULT_AES = {'y': '..y..'}
    CREATES = {'y'}

    @classmethod
    def compute_group(cls, data, scales, **params):
        # If n is None, use raw values; otherwise interpolate
        if params['n'] is None:
            x = np.unique(data['x'])
        else:
            x = np.linspace(data['x'].min(), data['x'].max(),
                            params['n'])

        y = ECDF(data['x'])(x)
        res = pd.DataFrame({'x': x, 'y': y})
        return res

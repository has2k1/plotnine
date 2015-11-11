from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
import pandas as pd

from ..utils import groupby_apply
from ..utils.exceptions import GgplotError
from ..scales.scale import scale_discrete
from .stat_summary import make_summary_fun
from .stat_bin_2d import bin_breaks
from .stat import stat


class stat_summary_bin(stat):
    REQUIRED_AES = {'x', 'y'}
    DEFAULT_PARAMS = {'geom': 'pointrange', 'position': 'identity',
                      'bins': 30, 'breaks': None, 'binwidth': None,
                      'origin': None, 'fun_data': None, 'fun_y': None,
                      'fun_ymin': None, 'fun_ymax': None,
                      'fun_args': dict()}

    def setup_params(self, data):
        keys = ('fun_data', 'fun_y', 'fun_ymin', 'fun_ymax')
        if not any(self.params[k] for k in keys):
            raise GgplotError('No summary function')

        return self.params

    @classmethod
    def compute_group(cls, data, scales, **params):
        bins = params['bins']
        breaks = params['breaks']
        binwidth = params['binwidth']
        origin = params['origin']

        func = make_summary_fun(params['fun_data'], params['fun_y'],
                                params['fun_ymin'], params['fun_ymax'],
                                params['fun_args'])

        breaks = bin_breaks(scales.x, breaks, origin, binwidth, bins)
        data['bin'] = pd.cut(data['x'], bins=breaks, labels=False,
                             include_lowest=True)

        def func_wrapper(data):
            res = func(data)
            res['bin'] = data['bin'].iloc[0]
            return res

        # This is a plyr::ddply
        out = groupby_apply(data, 'bin', func_wrapper)
        bin_centers = ((breaks[:-1] + breaks[1:])/2)[out['bin'].values]
        out['x'] = bin_centers
        out['bin'] += 1
        if isinstance(scales.x, scale_discrete):
            out['width'] = 0.9
        else:
            out['width'] = np.diff(breaks)[bins]

        return out

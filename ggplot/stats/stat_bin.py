from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from ..utils.exceptions import GgplotError, gg_warn
from .binning import (breaks_from_bins, breaks_from_binwidth,
                      assign_bins, freedman_diaconis_bins)
from .stat import stat


class stat_bin(stat):
    REQUIRED_AES = {'x'}
    DEFAULT_PARAMS = {'geom': 'histogram', 'position': 'stack',
                      'binwidth': None, 'bins': None,
                      'breaks': None, 'center': None,
                      'boundary': None, 'closed': 'right',
                      'pad': False}
    DEFAULT_AES = {'y': '..count..', 'weight': None}
    CREATES = {'y', 'width'}

    def setup_params(self, data):
        params = self.params

        if 'y' in data or 'y' in params:
            msg = "stat_bin() must not be used with a y aesthetic."
            raise GgplotError(msg)

        if data['x'].dtype.kind == 'i':
            msg = ("stat_bin requires a continuous x variable the x "
                   "variable is discrete. "
                   "Perhaps you want stat='count'?")
            raise GgplotError(msg)

        if params['closed'] not in ('right', 'left'):
            raise GgplotError(
                "`closed` should either 'right' or 'left'")

        if (params['breaks'] is None and
                params['binwidth'] is None and
                params['bins'] is None):
            params = params.copy()
            params['bins'] = freedman_diaconis_bins(data['x'])
            msg = ("'stat_bin()' using 'bins = {}'. "
                   "Pick better value with 'binwidth'.")
            gg_warn(msg.format(params['bins']))

        return params

    @classmethod
    def compute_group(cls, data, scales, **params):
        if params['breaks'] is not None:
            breaks = params['breaks']
        elif params['binwidth'] is not None:
            breaks = breaks_from_binwidth(
                scales.x.dimension(), params['binwidth'],
                params['center'], params['boundary'])
        else:
            breaks = breaks_from_bins(
                scales.x.dimension(), params['bins'],
                params['center'], params['boundary'])

        new_data = assign_bins(
            data['x'], breaks, data.get('weight'),
            params['pad'], params['closed'])
        return new_data

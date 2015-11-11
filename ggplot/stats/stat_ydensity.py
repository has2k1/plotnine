from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
import pandas as pd
import six

from ..utils import suppress
from ..utils.exceptions import GgplotError
from .stat_density import stat_density, compute_density
from .stat import stat


class stat_ydensity(stat):
    REQUIRED_AES = {'x', 'y'}
    DEFAULT_PARAMS = {'geom': 'violin', 'position': 'dodge',
                      'adjust': 1, 'kernel': 'gaussian',
                      'n': 1024, 'trim': True,
                      'scale': 'area'}
    DEFAULT_AES = {'weight': None}

    def setup_params(self, data):
        params = self.params.copy()

        valid_scale = ('area', 'count', 'width')
        if params['scale'] not in valid_scale:
            msg = "Parameter scale should be one of {}"
            raise GgplotError(msg.format(valid_scale))

        lookup = {
            'biweight': 'biw',
            'cosine': 'cos',
            'cosine2': 'cos2',
            'epanechnikov': 'epa',
            'gaussian': 'gau',
            'triangular': 'tri',
            'triweight': 'triw',
            'uniform': 'uni'}

        with suppress(KeyError):
            params['kernel'] = lookup[params['kernel'].lower()]

        if params['kernel'] not in six.viewvalues(lookup):
            msg = ("kernel should be one of {}. "
                   "You may use the abbreviations {}")
            raise GgplotError(msg.format(six.viewkeys(lookup),
                                         six.viewvalues()))

        missing_params = (six.viewkeys(stat_density.DEFAULT_PARAMS) -
                          six.viewkeys(params))
        for key in missing_params:
            params[key] = stat_density.DEFAULT_PARAMS[key]

        return params

    @classmethod
    def compute_panel(cls, data, scales, **params):
        data = super(cls, cls).compute_panel(data, scales, **params)

        if params['scale'] == 'area':
            data['violinwidth'] = data['density']/data['density'].max()
        elif params['scale'] == 'count':
            data['violinwidth'] = (data['density'].max() *
                                   data['n']/data['n'].max())
        elif params['scale'] == 'width':
            data['violinwidth'] = data['scaled']
        else:
            msg = "Unknown scale value '{}'"
            raise GgplotError(msg.format(params['scale']))

        return data

    @classmethod
    def compute_group(cls, data, scales, **params):
        n = len(data)

        if n < 3:
            return pd.DataFrame()

        weight = data.get('weight')

        if params['trim']:
            range_y = data['y'].min(), data['y'].max()
        else:
            range_y = scales.y.dimension()

        dens = compute_density(data['y'], weight, range_y, **params)
        dens['y'] = dens['x']
        dens['x'] = np.mean([data['x'].min(), data['x'].max()])

        # Compute width if x has multiple values
        if len(np.unique(data['x'])) > 1:
            dens['width'] = np.ptp(data['x']) * 0.9

        return dens

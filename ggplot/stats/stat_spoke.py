from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np

from .stat import stat


class stat_spoke(stat):
    REQUIRED_AES = {'x', 'y', 'angle', 'radius'}
    DEFAULT_PARAMS = {'geom': 'segment', 'position': 'identity'}
    DEFAULT_AES = {'xend': '..xend..', 'yend': '..yend..'}
    CREATES = {'xend', 'yend'}
    retransform = False

    @classmethod
    def _calculate_groups(cls, data, scales, **params):
        try:
            radius = data['radius']
        except KeyError:
            radius = params['radius']

        data['xend'] = data['x'] + np.cos(data['angle']) * radius
        data['yend'] = data['y'] + np.sin(data['angle']) * radius
        return data

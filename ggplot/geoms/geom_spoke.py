from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np

from .geom_segment import geom_segment


class geom_spoke(geom_segment):
    REQUIRED_AES = {'x', 'y', 'angle', 'radius'}

    def reparameterise(self, data):
        try:
            radius = data['radius']
        except KeyError:
            radius = self.aes_params['radius']

        data['xend'] = data['x'] + np.cos(data['angle']) * radius
        data['yend'] = data['y'] + np.sin(data['angle']) * radius
        return data

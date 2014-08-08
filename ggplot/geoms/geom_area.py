from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from .geom_ribbon import geom_ribbon


# An area plot is a special case of geom_ribbon,
# where the minimum of the range is fixed to 0,
# and the position adjustment defaults to 'stack'.

class geom_area(geom_ribbon):
    REQUIRED_AES = {'x', 'y'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'stack'}

    def reparameterise(self, data):
        data['ymin'] = 0
        data['ymax'] = data['y']
        return data

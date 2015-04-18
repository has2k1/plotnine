from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from ..scales.utils import resolution
from .geom_rect import geom_rect


class geom_tile(geom_rect):

    DEFAULT_AES = {'alpha': 1, 'color': None, 'fill': '#333333',
                   'linetype': 'solid', 'size': 0.1}
    REQUIRED_AES = {'x', 'y'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity'}

    _aes_renames = {'linetype': 'linestyle', 'size': 'linewidth',
                    'fill': 'facecolor', 'color': 'edgecolor'}

    def reparameterise(self, data):
        try:
            width = data.pop('width')
        except KeyError:
            width = resolution(data['x'], False)

        try:
            height = data.pop('height')
        except KeyError:
            height = resolution(data['y'], False)

        data['xmin'] = data['x'] - width / 2
        data['xmax'] = data['x'] + width / 2
        data['ymin'] = data['y'] - height / 2
        data['ymax'] = data['y'] + height / 2
        return data

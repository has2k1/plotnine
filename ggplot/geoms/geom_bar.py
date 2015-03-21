from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from .geom_rect import geom_rect


class geom_bar(geom_rect):
    DEFAULT_AES = {'alpha': 1, 'color': '', 'fill': '#333333',
                   'linetype': 'solid', 'size': 0.5,
                   'weight': 1}
    REQUIRED_AES = {'x'}
    DEFAULT_PARAMS = {'stat': 'bin', 'position': 'stack'}

    _extra_requires = {'y', 'width'}
    _aes_renames = {'linetype': 'linestyle', 'size': 'linewidth',
                    'fill': 'facecolor', 'color': 'edgecolor'}

    def reparameterise(self, data):
        bool_idx = (data['y'] < 0)

        data['ymin'] = 0
        data.loc[bool_idx, 'ymin'] = data.loc[bool_idx, 'y']

        data['ymax'] = data['y']
        data.loc[bool_idx, 'ymax'] = 0

        data['xmin'] = data['x'] - data['width'] / 2
        data['xmax'] = data['x'] + data['width'] / 2
        del data['width']
        return data

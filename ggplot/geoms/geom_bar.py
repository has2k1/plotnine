from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from ..scales.utils import resolution
from .geom_rect import geom_rect


class geom_bar(geom_rect):
    DEFAULT_AES = {'alpha': 1, 'color': None, 'fill': '#333333',
                   'linetype': 'solid', 'size': 1.5,
                   'weight': 1}
    REQUIRED_AES = {'x'}
    DEFAULT_PARAMS = {'stat': 'bar', 'position': 'stack',
                      'width': None}

    _extra_requires = {'y'}

    def setup_data(self, data):
        if 'width' not in data:
            if self.params['width']:
                data['width'] = self.params['width']
            else:
                data['width'] = resolution(data['x'], False) * 0.9

        bool_idx = (data['y'] < 0)

        data['ymin'] = 0
        data.loc[bool_idx, 'ymin'] = data.loc[bool_idx, 'y']

        data['ymax'] = data['y']
        data.loc[bool_idx, 'ymax'] = 0

        data['xmin'] = data['x'] - data['width'] / 2
        data['xmax'] = data['x'] + data['width'] / 2
        del data['width']
        return data

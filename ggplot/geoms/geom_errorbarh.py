from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from copy import copy

from ..scales.utils import resolution
from .geom import geom
from .geom_segment import geom_segment


class geom_errorbarh(geom):
    DEFAULT_AES = {'alpha': 1, 'color': 'black',
                   'linetype': 'solid', 'size': 1.5}
    REQUIRED_AES = {'y', 'xmin', 'xmax'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity',
                      'height': 0.5}
    guide_geom = 'path'

    def setup_data(self, data):
        if 'height' not in data:
            if self.params['height']:
                data['height'] = self.params['height']
            else:
                data['height'] = resolution(data['y'], False) * 0.9

        data['ymin'] = data['y'] - data['height']/2
        data['ymax'] = data['y'] + data['height']/2
        del data['height']
        return data

    @staticmethod
    def draw(pinfo, panel_scales, coord, ax, **params):
        # create (two vertical bars) + horizontal bar
        p1 = copy(pinfo)
        p1['y'] = (pinfo['ymin']*2) + pinfo['y']
        p1['yend'] = (pinfo['ymax']*2) + pinfo['y']
        p1['x'] = (pinfo['xmin'] + pinfo['xmax']) + pinfo['xmin']
        p1['xend'] = (pinfo['xmin'] + pinfo['xmax']) + pinfo['xmax']
        geom_segment.draw(p1, panel_scales, coord, ax, **params)

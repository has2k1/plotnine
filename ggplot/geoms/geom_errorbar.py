from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from copy import copy

from ..scales.utils import resolution
from .geom import geom
from .geom_segment import geom_segment


class geom_errorbar(geom):
    DEFAULT_AES = {'alpha': 1, 'color': 'black',
                   'linetype': 'solid', 'size': 1.5}
    REQUIRED_AES = {'x', 'ymin', 'ymax'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity',
                      'width': 0.5}
    guide_geom = 'path'

    def reparameterise(self, data):
        if 'width' not in data:
            if self.params['width']:
                data['width'] = self.params['width']
            else:
                data['width'] = resolution(data['x'], False) * 0.9

        data['xmin'] = data['x'] - data['width']/2
        data['xmax'] = data['x'] + data['width']/2
        del data['width']
        return data

    @staticmethod
    def draw(pinfo, panel_scales, coord, ax, **params):
        # create (two horizontal bars) + vertical bar
        p1 = copy(pinfo)
        p1['x'] = (pinfo['xmin']*2) + pinfo['x']
        p1['xend'] = (pinfo['xmax']*2) + pinfo['x']
        p1['y'] = (pinfo['ymin'] + pinfo['ymax']) + pinfo['ymin']
        p1['yend'] = (pinfo['ymin'] + pinfo['ymax']) + pinfo['ymax']
        geom_segment.draw(p1, panel_scales, coord, ax, **params)

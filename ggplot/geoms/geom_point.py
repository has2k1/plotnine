from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from ..utils import make_color_tuples
from .geom import geom


class geom_point(geom):
    DEFAULT_AES = {'alpha': 1, 'color': 'black', 'fill': None,
                   'shape': 'o', 'size': 20}
    REQUIRED_AES = {'x', 'y'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity'}

    _aes_renames = {'size': 's', 'shape': 'marker', 'fill': 'facecolor'}
    _units = {'marker'}

    def draw_groups(self, data, scales, ax, **kwargs):
        """
        Plot all groups
        """
        pinfos = self._make_pinfos(data, kwargs)
        for pinfo in pinfos:
            self.draw(pinfo, scales, ax, **kwargs)

    @staticmethod
    def draw(pinfo, scales, ax, **kwargs):
        fc = pinfo['facecolor']
        if fc is None:
            # default to color
            pinfo['facecolor'] = pinfo['color']
        elif fc is False:
            # Matplotlib expects empty string instead of False
            pinfo['facecolor'] = ''
        else:
            pinfo['facecolor'] = make_color_tuples(
                pinfo['facecolor'], pinfo['alpha'])

        ax.scatter(**pinfo)

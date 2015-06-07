from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from ..utils import make_rgba
from .geom import geom


class geom_vline(geom):
    DEFAULT_AES = {'color': 'black', 'linetype': 'solid',
                   'size': 1.0, 'alpha': 1, 'x': None,
                   'ymin': None, 'ymax': None}
    REQUIRED_AES = {'xintercept'}
    DEFAULT_PARAMS = {'stat': 'vline', 'position': 'identity',
                      'show_guide': False,
                      'inherit_aes': False}
    guide_geom = 'path'

    _aes_renames = {'size': 'linewidth', 'linetype': 'linestyle'}

    def draw_groups(self, data, scales, coordinates, ax, **params):
        """
        Plot all groups
        """
        pinfos = self._make_pinfos(data, params)
        for pinfo in pinfos:
            self.draw(pinfo, scales, coordinates, ax, **params)

    @staticmethod
    def draw(pinfo, scales, coordinates, ax, **params):
        try:
            del pinfo['x']
        except KeyError:
            pass
        x = pinfo.pop('xintercept')
        ymin = pinfo.pop('ymin')
        ymax = pinfo.pop('ymax')

        ranges = coordinates.range(scales)
        if ymin is None:
            ymin = ranges.y[0]

        if ymax is None:
            ymax = ranges.y[1]

        alpha = pinfo.pop('alpha')
        pinfo['color'] = make_rgba(pinfo['color'], alpha)
        del pinfo['group']
        ax.vlines(x, ymin, ymax, **pinfo)

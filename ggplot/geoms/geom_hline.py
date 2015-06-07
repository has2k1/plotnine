from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from ..utils import make_rgba
from .geom import geom


class geom_hline(geom):
    DEFAULT_AES = {'color': 'black', 'linetype': 'solid',
                   'size': 1.0, 'alpha': 1, 'y': None,
                   'xmin': None, 'xmax': None}
    REQUIRED_AES = {'yintercept'}
    DEFAULT_PARAMS = {'stat': 'hline', 'position': 'identity',
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
            del pinfo['y']
        except KeyError:
            pass
        y = pinfo.pop('yintercept')
        xmin = pinfo.pop('xmin')
        xmax = pinfo.pop('xmax')

        ranges = coordinates.range(scales)
        if xmin is None:
            xmin = ranges.x[0]

        if xmax is None:
            xmax = ranges.x[1]

        alpha = pinfo.pop('alpha')
        pinfo['color'] = make_rgba(pinfo['color'], alpha)
        del pinfo['group']
        ax.hlines(y, xmin, xmax, **pinfo)

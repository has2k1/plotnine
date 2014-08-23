from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from .geom import geom


class geom_ribbon(geom):
    DEFAULT_AES = {'alpha': 1, 'color': None, 'fill': '#333333',
                   'linetype': 'solid', 'size': 1.0}
    REQUIRED_AES = {'x', 'ymax', 'ymin'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity'}

    _aes_renames = {'linetype': 'linestyle', 'ymin': 'y1', 'ymax': 'y2',
                    'size': 'linewidth', 'fill': 'facecolor',
                    'color': 'edgecolor'}
    _units = {'alpha', 'edgecolor', 'facecolor', 'linestyle', 'linewidth'}

    def draw_groups(self, data, scales, ax, **kwargs):
        """
        Plot all groups
        """
        pinfos = self._make_pinfos(data)
        for pinfo in pinfos:
            self.draw(pinfo, scales, ax, **kwargs)

    def draw(self, pinfo, scales, ax, **kwargs):
        try:
            del pinfo['y']
        except KeyError:
            pass

        ax.fill_between(**pinfo)

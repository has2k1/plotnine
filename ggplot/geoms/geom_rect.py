from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from matplotlib.collections import PolyCollection

from ..utils import make_iterable, make_color_tuples
from .geom import geom


class geom_rect(geom):
    """
    Draw a rectangle on a plot.

    Notes
    -----
    geom_rect accepts the following aesthetics (* - required):
    xmax *
    xmin *
    ymax *
    ymin *
    alpha
    colour
    fill
    linetype
    size
    """

    DEFAULT_AES = {'color': None, 'fill': '#333333',
                   'linetype': 'solid', 'size': 1.0, 'alpha': 1}

    REQUIRED_AES = {'xmax', 'xmin', 'ymax', 'ymin'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity'}
    guide_geom = 'polygon'

    _aes_renames = {'size': 'linewidth', 'linetype': 'linestyle',
                    'fill': 'facecolor', 'color': 'edgecolor'}

    def draw_groups(self, data, scales, ax, **kwargs):
        """
        Plot all groups
        """
        pinfos = self._make_pinfos(data, kwargs)
        for pinfo in pinfos:
            self.draw(pinfo, scales, ax, **kwargs)

    @staticmethod
    def draw(pinfo, scales, ax, **kwargs):
        def fn(key):
            return make_iterable(pinfo.pop(key))

        xmin = fn('xmin')
        xmax = fn('xmax')
        ymin = fn('ymin')
        ymax = fn('ymax')

        verts = [None] * len(xmin)
        for i in range(len(xmin)):
            verts[i] = [(xmin[i], ymin[i]),
                        (xmin[i], ymax[i]),
                        (xmax[i], ymax[i]),
                        (xmax[i], ymin[i])]

        pinfo['facecolor'] = make_color_tuples(
            pinfo['facecolor'], pinfo['alpha'])

        if pinfo['edgecolor'] is None:
            pinfo['edgecolor'] = ''

        col = PolyCollection(
            verts,
            facecolors=pinfo['facecolor'],
            edgecolors=pinfo['edgecolor'],
            linestyles=pinfo['linestyle'],
            linewidths=pinfo['linewidth'],
            transOffset=ax.transData,
            zorder=pinfo['zorder']
        )
        ax.add_collection(col)

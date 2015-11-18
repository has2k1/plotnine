from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from matplotlib.collections import PolyCollection
from six.moves import zip

from ..utils import make_iterable, to_rgba
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

    DEFAULT_AES = {'color': None, 'fill': '#595959',
                   'linetype': 'solid', 'size': 1.5, 'alpha': 1}

    REQUIRED_AES = {'xmax', 'xmin', 'ymax', 'ymin'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity'}
    legend_geom = 'polygon'

    def draw_panel(self, data, panel_scales, coord, ax, **params):
        """
        Plot all groups
        """
        pinfos = self._make_pinfos(data, params)
        for pinfo in pinfos:
            self.draw_group(pinfo, panel_scales, coord, ax, **params)

    @staticmethod
    def draw_group(pinfo, panel_scales, coord, ax, **params):
        def fn(key):
            return make_iterable(pinfo.pop(key))

        xmin = fn('xmin')
        xmax = fn('xmax')
        ymin = fn('ymin')
        ymax = fn('ymax')

        verts = [None] * len(xmin)
        limits = zip(xmin, xmax, ymin, ymax)
        for i, (l, r, b, t) in enumerate(limits):
            verts[i] = [(l, b), (l, t), (r, t), (r, b)]

        pinfo['fill'] = to_rgba(pinfo['fill'], pinfo['alpha'])
        pinfo['color'] = to_rgba(pinfo['color'], pinfo['alpha'])

        if pinfo['color'] is None:
            pinfo['color'] = ''

        col = PolyCollection(
            verts,
            facecolors=pinfo['fill'],
            edgecolors=pinfo['color'],
            linestyles=pinfo['linetype'],
            linewidths=pinfo['size'],
            transOffset=ax.transData,
            zorder=pinfo['zorder'])
        ax.add_collection(col)

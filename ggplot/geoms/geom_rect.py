from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from matplotlib.collections import PolyCollection
from six.moves import zip

from ..utils import to_rgba
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
        self.draw_group(data, panel_scales, coord, ax, **params)

    @staticmethod
    def draw_group(data, panel_scales, coord, ax, **params):
        data = coord.transform(data, panel_scales, munch=True)
        verts = [None] * len(data)
        limits = zip(data['xmin'], data['xmax'],
                     data['ymin'], data['ymax'])

        for i, (l, r, b, t) in enumerate(limits):
            verts[i] = [(l, b), (l, t), (r, t), (r, b)]

        fill = to_rgba(data['fill'], data['alpha'])
        color = to_rgba(data['color'], data['alpha'])

        if color is None:
            color = ''

        col = PolyCollection(
            verts,
            facecolors=fill,
            edgecolors=color,
            linestyles=data['linetype'].tolist(),
            linewidths=data['size'].tolist(),
            transOffset=ax.transData,
            zorder=params['zorder'])
        ax.add_collection(col)

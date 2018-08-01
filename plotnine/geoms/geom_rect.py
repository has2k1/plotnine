from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from matplotlib.collections import PolyCollection
from six.moves import zip
import numpy as np

from ..utils import to_rgba, SIZE_FACTOR
from ..doctools import document
from .geom import geom


@document
class geom_rect(geom):
    """
    Rectangles

    {usage}

    Parameters
    ----------
    {common_parameters}
    """

    DEFAULT_AES = {'color': None, 'fill': '#595959',
                   'linetype': 'solid', 'size': 0.5, 'alpha': 1}
    REQUIRED_AES = {'xmax', 'xmin', 'ymax', 'ymin'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity',
                      'na_rm': False}
    legend_geom = 'polygon'

    def draw_panel(self, data, panel_params, coord, ax, **params):
        """
        Plot all groups
        """
        self.draw_group(data, panel_params, coord, ax, **params)

    @staticmethod
    def draw_group(data, panel_params, coord, ax, **params):
        data = coord.transform(data, panel_params, munch=True)
        data['size'] *= SIZE_FACTOR
        verts = [None] * len(data)

        # Make it easy to specify rects that fill the x|y range
        xlimits = panel_params['x_range']
        ylimits = panel_params['y_range']
        data['xmin'].replace(-np.inf, xlimits[0], inplace=True)
        data['xmax'].replace(np.inf, xlimits[1], inplace=True)
        data['ymin'].replace(-np.inf, ylimits[0], inplace=True)
        data['ymax'].replace(np.inf, ylimits[1], inplace=True)

        limits = zip(data['xmin'], data['xmax'],
                     data['ymin'], data['ymax'])

        for i, (l, r, b, t) in enumerate(limits):
            verts[i] = [(l, b), (l, t), (r, t), (r, b)]

        fill = to_rgba(data['fill'], data['alpha'])
        color = data['color']

        # prevent unnecessary borders
        if all(color.isnull()):
            color = 'none'

        col = PolyCollection(
            verts,
            facecolors=fill,
            edgecolors=color,
            linestyles=data['linetype'],
            linewidths=data['size'],
            transOffset=ax.transData,
            zorder=params['zorder'])
        ax.add_collection(col)

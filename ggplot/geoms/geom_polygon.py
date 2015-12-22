from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
import pandas as pd
from matplotlib.collections import PolyCollection
from matplotlib.patches import Rectangle

from ..utils import to_rgba
from .geom import geom


class geom_polygon(geom):
    DEFAULT_AES = {'alpha': 1, 'color': None, 'fill': '#333333',
                   'linetype': 'solid', 'size': 1.5}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity'}
    REQUIRED_AES = {'x', 'y'}
    _munch = True

    def draw_panel(self, data, panel_scales, coord, ax, **params):
        """
        Plot all groups
        """
        data = coord.transform(data, panel_scales, self._munch)
        pinfos = self._make_pinfos(data, params)
        for pinfo in pinfos:
            self.draw_group(pinfo, panel_scales, coord, ax, **params)

    @staticmethod
    def draw_group(pinfo, panel_scales, coord, ax, **params):
        # Each group is a polygon with a single facecolor
        # with potentially an edgecolor for every edge.
        grouped = pd.DataFrame(pinfo).groupby('group')
        verts = [None] * grouped.ngroups
        facecolor = [None] * grouped.ngroups
        edgecolor = [None] * grouped.ngroups
        for i, (group, df) in enumerate(grouped):
            verts[i] = tuple(zip(df['x'], df['y']))
            fill = to_rgba(df['fill'].iloc[0], df['alpha'].iloc[0])
            color = to_rgba(df['color'].iloc[0], df['alpha'].iloc[0])
            facecolor[i] = 'none' if fill is None else fill
            edgecolor[i] = 'none' if color is None else color

        col = PolyCollection(
            verts,
            facecolors=facecolor,
            edgecolors=edgecolor,
            linestyles=pinfo['linetype'],
            linewidths=pinfo['size'],
            transOffset=ax.transData,
            zorder=pinfo['zorder']
        )
        ax.add_collection(col)

    @staticmethod
    def draw_legend(data, da, lyr):
        """
        Draw a rectangle in the box

        Parameters
        ----------
        data : dataframe
        da : DrawingArea
        lyr : layer

        Returns
        -------
        out : DrawingArea
        """
        # We take into account that the linewidth
        # bestrides the boundary of the rectangle
        linewidth = np.min([data['size'],
                            da.width/4, da.height/4])
        if data['color'] is None:
            linewidth = 0

        if data['fill'] is None:
            data['fill'] = 'none'

        rect = Rectangle((0+linewidth/2, 0+linewidth/2),
                         width=da.width-linewidth,
                         height=da.height-linewidth,
                         linewidth=linewidth,
                         linestyle=data['linetype'],
                         alpha=data['alpha'],
                         facecolor=data['fill'],
                         edgecolor=data['color'],
                         capstyle='projecting')
        da.add_artist(rect)
        return da

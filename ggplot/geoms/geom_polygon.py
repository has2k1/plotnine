from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
from matplotlib.collections import PolyCollection
from matplotlib.patches import Rectangle

from ..utils import to_rgba, SIZE_FACTOR
from .geom import geom


class geom_polygon(geom):
    DEFAULT_AES = {'alpha': 1, 'color': None, 'fill': '#333333',
                   'linetype': 'solid', 'size': 0.5}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity'}
    REQUIRED_AES = {'x', 'y'}

    def draw_panel(self, data, panel_scales, coord, ax, **params):
        """
        Plot all groups
        """
        self.draw_group(data, panel_scales, coord, ax, **params)

    @staticmethod
    def draw_group(data, panel_scales, coord, ax, **params):
        data = coord.transform(data, panel_scales, munch=True)
        data['size'] *= SIZE_FACTOR

        # Each group is a polygon with a single facecolor
        # with potentially an edgecolor for every edge.
        ngroups = data['group'].unique().size
        verts = [None] * ngroups
        facecolor = [None] * ngroups
        edgecolor = [None] * ngroups
        linestyle = [None] * ngroups
        linewidth = [None] * ngroups

        for i, (group, df) in enumerate(data.groupby('group')):
            verts[i] = tuple(zip(df['x'], df['y']))
            fill = to_rgba(df['fill'].iloc[0], df['alpha'].iloc[0])
            color = to_rgba(df['color'].iloc[0], df['alpha'].iloc[0])
            facecolor[i] = 'none' if fill is None else fill
            edgecolor[i] = 'none' if color is None else color
            linestyle[i] = df['linetype'].iloc[0]
            linewidth[i] = df['size'].iloc[0]

        col = PolyCollection(
            verts,
            facecolors=facecolor,
            edgecolors=edgecolor,
            linestyles=linestyle,
            linewidths=linewidth,
            transOffset=ax.transData,
            zorder=params['zorder'])

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
        data['size'] *= SIZE_FACTOR
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

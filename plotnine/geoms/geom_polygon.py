from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
from matplotlib.collections import PolyCollection
from matplotlib.patches import Rectangle

from ..utils import to_rgba, SIZE_FACTOR
from ..doctools import document
from .geom import geom


@document
class geom_polygon(geom):
    """
    Polygon, a filled path

    {usage}

    Parameters
    ----------
    {common_parameters}

    {aesthetics}

    All paths in the same ``group`` aesthetic value make up a polygon.
    """
    DEFAULT_AES = {'alpha': 1, 'color': None, 'fill': '#333333',
                   'linetype': 'solid', 'size': 0.5}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity',
                      'na_rm': False}
    REQUIRED_AES = {'x', 'y'}

    def handle_na(self, data):
        return data

    def draw_panel(self, data, panel_params, coord, ax, **params):
        """
        Plot all groups
        """
        self.draw_group(data, panel_params, coord, ax, **params)

    @staticmethod
    def draw_group(data, panel_params, coord, ax, **params):
        data = coord.transform(data, panel_params, munch=True)
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
            facecolor[i] = 'none' if fill is None else fill
            edgecolor[i] = df['color'].iloc[0] or 'none'
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

        facecolor = to_rgba(data['fill'], data['alpha'])
        if facecolor is None:
            facecolor = 'none'

        rect = Rectangle((0+linewidth/2, 0+linewidth/2),
                         width=da.width-linewidth,
                         height=da.height-linewidth,
                         linewidth=linewidth,
                         linestyle=data['linetype'],
                         facecolor=facecolor,
                         edgecolor=data['color'],
                         capstyle='projecting')
        da.add_artist(rect)
        return da

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
import pandas as pd
from matplotlib.collections import PolyCollection
from matplotlib.patches import Rectangle

from ..utils import to_rgba, make_iterable
from .geom import geom


class geom_polygon(geom):
    DEFAULT_AES = {'alpha': 1, 'color': None, 'fill': '#333333',
                   'linetype': 'solid', 'size': 1.5}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity'}
    REQUIRED_AES = {'x', 'y'}

    def draw_panel(self, data, panel_scales, coord, ax, **params):
        """
        Plot all groups
        """
        pinfos = self._make_pinfos(data, params)
        for pinfo in pinfos:
            self.draw_group(pinfo, panel_scales, coord, ax, **params)

    @staticmethod
    def draw_group(pinfo, panel_scales, coord, ax, **params):
        # Each group is a polygon with a single facecolor
        # with potentially an edgecolor for every edge.
        # And like ggplot, alpha applies to the facecolor
        # and not the edgecolor
        grouped = pd.DataFrame(pinfo).groupby('group')
        verts, facecolor = [], []
        for group, df in grouped:
            verts.append(tuple(zip(df['x'], df['y'])))
            fc = to_rgba(df['fill'].iloc[0], df['alpha'].iloc[0])
            facecolor.append('none' if fc is None else fc)

        edgecolor = ['none' if c is None else c
                     for c in make_iterable(pinfo['color'])]

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

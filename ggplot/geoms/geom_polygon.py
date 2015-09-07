from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pandas as pd
from matplotlib.collections import PolyCollection
from matplotlib.patches import Rectangle
import matplotlib.lines as lines

from ..utils import to_rgba, make_iterable
from .geom import geom


class geom_polygon(geom):
    DEFAULT_AES = {'alpha': 1, 'color': None, 'fill': '#333333',
                   'linetype': 'solid', 'size': 1.5}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity'}
    REQUIRED_AES = {'x', 'y'}

    def draw_groups(self, data, scales, coordinates, ax, **params):
        """
        Plot all groups
        """
        pinfos = self._make_pinfos(data, params)
        for pinfo in pinfos:
            self.draw(pinfo, scales, coordinates, ax, **params)

    @staticmethod
    def draw(pinfo, scales, coordinates, ax, **params):
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
        # ggplot leaves out the linetpe when drawing the
        # rectangle despite being helpful in some cases.
        # We check if linetype is mapped to in the layer
        # responsible for this legend entry, and
        # only then do we include it
        kwargs = {}
        if 'linetype' in lyr._active_mapping:
            kwargs['linestyle'] = data['linetype']

        # background
        facecolor = to_rgba(data['fill'], data['alpha'])
        if facecolor is None:
            facecolor = 'none'
        bg = Rectangle((0, 0),
                       width=da.width,
                       height=da.height,
                       facecolor=facecolor,
                       edgecolor=data['color'],
                       capstyle='projecting',
                       **kwargs)
        da.add_artist(bg)

        # diagonal strike through
        if data['color']:
            strike = lines.Line2D([0, da.width],
                                  [0, da.height],
                                  linestyle=data['linetype'],
                                  linewidth=data['size'],
                                  color=data['color'],
                                  solid_capstyle='butt')
            da.add_artist(strike)
        return da

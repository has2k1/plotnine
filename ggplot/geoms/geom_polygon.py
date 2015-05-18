from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pandas as pd
from matplotlib.collections import PolyCollection
from matplotlib.patches import Rectangle
import matplotlib.lines as lines

from ..utils import make_color_tuples, make_iterable
from .geom import geom


class geom_polygon(geom):
    DEFAULT_AES = {'alpha': 1, 'color': None, 'fill': '#333333',
                   'linetype': 'solid', 'size': 0.5}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity'}
    REQUIRED_AES = {'x', 'y'}
    guide_geom = 'polygon'

    _aes_renames = {'size': 'linewidth', 'linetype': 'linestyle',
                    'fill': 'facecolor', 'color': 'edgecolor'}

    def draw_groups(self, data, scales, coordinates, ax, **kwargs):
        """
        Plot all groups
        """
        pinfos = self._make_pinfos(data, kwargs)
        for pinfo in pinfos:
            self.draw(pinfo, scales, coordinates, ax, **kwargs)

    @staticmethod
    def draw(pinfo, scales, coordinates, ax, **kwargs):
        # Each group is a polygon with a single facecolor
        # with potentially an edgecolor for every edge.
        # And like ggplot, alpha applies to the facecolor
        # and not the edgecolor
        grouped = pd.DataFrame(pinfo).groupby('group')
        verts, fc, alpha = [], [], []
        for group, df in grouped:
            verts.append(tuple(zip(df['x'], df['y'])))
            fc.append(df['facecolor'].iloc[0])
            alpha.append(df['alpha'].iloc[0])

        fc = make_color_tuples(fc, alpha)
        ec = ['none' if c is None else c
              for c in make_iterable(pinfo['edgecolor'])]

        col = PolyCollection(
            verts,
            facecolors=fc,
            edgecolors=ec,
            linestyles=pinfo['linestyle'],
            linewidths=pinfo['linewidth'],
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
            kwargs['linestyle'] = data['linestyle']

        # background
        fc = make_color_tuples(data['facecolor'], data['alpha'])
        if fc is None:
            fc = 'none'
        bg = Rectangle((0, 0),
                       width=da.width,
                       height=da.height,
                       facecolor=fc,
                       edgecolor=data['edgecolor'],
                       **kwargs)
        da.add_artist(bg)

        # diagonal strike through
        if data['edgecolor']:
            strike = lines.Line2D([0, da.width],
                                  [0, da.height],
                                  linestyle=data['linestyle'],
                                  linewidth=data['linewidth'],
                                  color=data['edgecolor'],
                                  solid_capstyle='butt')
            da.add_artist(strike)
        return da

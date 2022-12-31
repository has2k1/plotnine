from __future__ import annotations

import typing

import numpy as np
from matplotlib.collections import PolyCollection
from matplotlib.patches import Rectangle

from ..doctools import document
from ..utils import SIZE_FACTOR, to_rgba
from .geom import geom

if typing.TYPE_CHECKING:
    from typing import Any

    import matplotlib as mpl
    import pandas as pd

    import plotnine as p9


@document
class geom_polygon(geom):
    """
    Polygon, a filled path

    {usage}

    Parameters
    ----------
    {common_parameters}

    Notes
    -----
    All paths in the same ``group`` aesthetic value make up a polygon.
    """
    DEFAULT_AES = {'alpha': 1, 'color': None, 'fill': '#333333',
                   'linetype': 'solid', 'size': 0.5}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity',
                      'na_rm': False}
    REQUIRED_AES = {'x', 'y'}

    def handle_na(self, data: pd.DataFrame) -> pd.DataFrame:
        return data

    def draw_panel(
        self,
        data: pd.DataFrame,
        panel_params: p9.iapi.panel_view,
        coord: p9.coords.coord.coord,
        ax: mpl.axes.Axes,
        **params: Any
    ) -> None:
        """
        Plot all groups
        """
        self.draw_group(data, panel_params, coord, ax, **params)

    @staticmethod
    def draw_group(
        data: pd.DataFrame,
        panel_params: p9.iapi.panel_view,
        coord: p9.coords.coord.coord,
        ax: mpl.axes.Axes,
        **params: Any
    ) -> None:
        data = coord.transform(data, panel_params, munch=True)
        data['size'] *= SIZE_FACTOR

        # Each group is a polygon with a single facecolor
        # with potentially an edgecolor for every edge.
        verts = []
        facecolor = []
        edgecolor = []
        linestyle = []
        linewidth = []

        # Some stats may order the data in ways that prevent
        # objects from occluding other objects. We do not want
        # to undo that order.
        grouper = data.groupby('group', sort=False)
        for group, df in grouper:
            fill = to_rgba(df['fill'].iloc[0], df['alpha'].iloc[0])
            verts.append(tuple(zip(df['x'], df['y'])))
            facecolor.append('none' if fill is None else fill)
            edgecolor.append(df['color'].iloc[0] or 'none')
            linestyle.append(df['linetype'].iloc[0])
            linewidth.append(df['size'].iloc[0])

        col = PolyCollection(
            verts,
            facecolors=facecolor,
            edgecolors=edgecolor,
            linestyles=linestyle,
            linewidths=linewidth,
            zorder=params['zorder'],
            rasterized=params['raster'],
        )

        ax.add_collection(col)

    @staticmethod
    def draw_legend(
        data: pd.Series[Any],
        da: mpl.patches.DrawingArea,
        lyr: p9.layer.layer
    ) -> mpl.patches.DrawingArea:
        """
        Draw a rectangle in the box

        Parameters
        ----------
        data : Series
            Data Row
        da : DrawingArea
            Canvas
        lyr : layer
            Layer

        Returns
        -------
        out : DrawingArea
        """
        data['size'] *= SIZE_FACTOR
        # We take into account that the linewidth
        # bestrides the boundary of the rectangle
        linewidth = np.min([data['size'], da.width/4, da.height/4])

        if data['color'] is None:
            linewidth = 0

        facecolor = to_rgba(data['fill'], data['alpha'])
        if facecolor is None:
            facecolor = 'none'

        rect = Rectangle(
            (0+linewidth/2, 0+linewidth/2),
            width=da.width-linewidth,
            height=da.height-linewidth,
            linewidth=linewidth,
            linestyle=data['linetype'],
            facecolor=facecolor,
            edgecolor=data['color'],
            capstyle='projecting'
        )
        da.add_artist(rect)
        return da

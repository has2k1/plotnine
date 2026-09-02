from __future__ import annotations

import typing

import numpy as np

from .._utils import SIZE_FACTOR, to_rgba
from ..doctools import document
from .geom import geom
from .geom_path import geom_path

if typing.TYPE_CHECKING:
    from typing import Any

    import numpy.typing as npt
    import pandas as pd
    from matplotlib.axes import Axes
    from matplotlib.offsetbox import DrawingArea
    from matplotlib.path import Path

    from plotnine.coords.coord import coord
    from plotnine.iapi import panel_view
    from plotnine.layer import layer


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
    All paths in the same `group` aesthetic value make up a polygon.
    """

    _aesthetics_doc = """
    {aesthetics_table}

    **Aesthetics Descriptions**

    `subgroup`

    :   Identify the rings within one `group`. The first ring forms the
        exterior; each later ring with the opposite winding direction
        forms a hole.
    """

    DEFAULT_AES = {
        "alpha": 1,
        "color": None,
        "fill": "#333333",
        "linetype": "solid",
        "size": 0.5,
    }
    REQUIRED_AES = {"x", "y"}

    legend_key_size = staticmethod(geom_path.legend_key_size)

    def handle_na(self, data: pd.DataFrame) -> pd.DataFrame:
        return data

    def draw_panel(
        self,
        data: pd.DataFrame,
        panel_params: panel_view,
        coord: coord,
        ax: Axes,
    ):
        """
        Plot all groups
        """
        self.draw_group(data, panel_params, coord, ax, self.params)

    @staticmethod
    def draw_group(
        data: pd.DataFrame,
        panel_params: panel_view,
        coord: coord,
        ax: Axes,
        params: dict[str, Any],
    ):
        from matplotlib.collections import PathCollection, PolyCollection

        # Polygon vertices omit the closing edge. Non-linear coordinates
        # must interpolate that edge with the others; otherwise a curved
        # boundary closes with a straight chord. Append each ring's first
        # vertex before transformation. Linear coordinates already close
        # the ring correctly.
        if not coord.is_linear:
            by = ["group", "subgroup"] if "subgroup" in data else "group"
            indices = data.groupby(by, sort=False).indices
            order = np.concatenate(
                [np.append(idx, idx[0]) for idx in indices.values()]
            )
            data = data.iloc[order].reset_index(drop=True)

        data = coord.transform(data, panel_params, munch=True)
        data["linewidth"] = data["size"] * SIZE_FACTOR

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
        has_holes = "subgroup" in data
        grouper = data.groupby("group", sort=False)
        for group, df in grouper:
            fill = to_rgba(df["fill"].iloc[0], df["alpha"].iloc[0])
            if has_holes:
                verts.append(
                    compound_path(
                        [
                            ring[["x", "y"]].to_numpy()
                            for _, ring in df.groupby("subgroup", sort=False)
                        ]
                    )
                )
            else:
                verts.append(tuple(zip(df["x"], df["y"])))
            facecolor.append("none" if fill is None else fill)
            edgecolor.append(df["color"].iloc[0] or "none")
            linestyle.append(df["linetype"].iloc[0])
            linewidth.append(df["linewidth"].iloc[0])

        cls = PathCollection if has_holes else PolyCollection
        col = cls(
            verts,
            facecolors=facecolor,
            edgecolors=edgecolor,
            linestyles=linestyle,
            linewidths=linewidth,
            zorder=params["zorder"],
            rasterized=params["raster"],
        )

        ax.add_collection(col)

    @staticmethod
    def draw_legend(
        data: pd.Series[Any], da: DrawingArea, lyr: layer
    ) -> DrawingArea:
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
        from matplotlib.patches import Rectangle

        # We take into account that the linewidth
        # bestrides the boundary of the rectangle
        linewidth = data["size"] * SIZE_FACTOR
        linewidth = np.min([linewidth, da.width / 4, da.height / 4])

        if data["color"] is None:
            linewidth = 0

        facecolor = to_rgba(data["fill"], data["alpha"])
        if facecolor is None:
            facecolor = "none"

        rect = Rectangle(
            (0 + linewidth / 2, 0 + linewidth / 2),
            width=da.width - linewidth,
            height=da.height - linewidth,
            linewidth=linewidth,
            linestyle=data["linetype"],
            facecolor=facecolor,
            edgecolor=data["color"],
            capstyle="projecting",
        )
        da.add_artist(rect)
        return da


def compound_path(rings: list[npt.NDArray[Any]]) -> Path:
    """
    Combine polygon rings into one path

    Under the non-zero winding rule, a ring whose direction opposes its
    enclosing ring forms a hole.
    """
    from matplotlib.path import Path

    vertices = np.concatenate([np.vstack([r, r[:1]]) for r in rings])
    codes = np.concatenate(
        [
            [Path.MOVETO, *[Path.LINETO] * (len(r) - 1), Path.CLOSEPOLY]
            for r in rings
        ]
    )
    return Path(vertices, codes)

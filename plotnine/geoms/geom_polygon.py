from __future__ import annotations

import typing

import narwhals as nw
import numpy as np

from .._utils import SIZE_FACTOR, frame, to_rgba
from ..doctools import document
from .geom import geom
from .geom_path import geom_path

if typing.TYPE_CHECKING:
    from typing import Any

    import numpy.typing as npt
    from matplotlib.axes import Axes
    from matplotlib.offsetbox import DrawingArea
    from matplotlib.path import Path

    from plotnine._utils.frame import DataFrame
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

    def handle_na(self, data: DataFrame) -> DataFrame:
        return data

    def draw_panel(
        self,
        data: DataFrame,
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
        data: DataFrame,
        panel_params: panel_view,
        coord: coord,
        ax: Axes,
        params: dict[str, Any],
    ):
        from matplotlib.collections import PathCollection, PolyCollection

        has_subgroups = "subgroup" in data.columns
        if not coord.is_linear:
            # Close each ring before munching. Matplotlib closes the
            # transformed polygon with a straight segment; we need the
            # closing edge to be curved in the transformed space too.
            by = ["group", "subgroup"] if has_subgroups else "group"
            indices = frame.group_indices(
                data, by, drop_missing=False, sort=False
            )
            order = np.concatenate([np.append(idx, idx[0]) for idx in indices])
            data = frame.take(data, order)

        data = coord.transform(data, panel_params, munch=True)
        data = data.with_columns(linewidth=nw.col("size") * SIZE_FACTOR)

        # Each group is a polygon with a single facecolor
        # with potentially an edgecolor for every edge.
        polygons = []
        facecolor = []
        edgecolor = []
        linestyle = []
        linewidth = []

        # Some stats may order the data in ways that prevent
        # objects from occluding other objects. We do not want
        # to undo that order.
        for _, df in frame.group_split(data, "group", sort=False):
            fill = to_rgba(df["fill"].item(0), df["alpha"].item(0))
            if has_subgroups:
                rings = frame.group_split(
                    df, "subgroup", drop_missing=False, sort=False
                )
                polygons.append(
                    compound_path(
                        [ring.select("x", "y").to_numpy() for _, ring in rings]
                    )
                )
            else:
                polygons.append(
                    tuple(
                        zip(frame.to_numpy(df["x"]), frame.to_numpy(df["y"]))
                    )
                )
            facecolor.append("none" if fill is None else fill)
            edgecolor.append(df["color"].item(0) or "none")
            linestyle.append(df["linetype"].item(0))
            linewidth.append(df["linewidth"].item(0))

        cls = PathCollection if has_subgroups else PolyCollection
        col = cls(
            polygons,
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
        data: dict[str, Any], da: DrawingArea, lyr: layer
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

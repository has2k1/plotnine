from __future__ import annotations

import typing
from collections import Counter
from contextlib import suppress
from warnings import warn

import numpy as np

from .._utils import SIZE_FACTOR, make_line_segments, match, to_rgba
from ..doctools import document
from ..exceptions import PlotnineWarning
from .geom import geom

if typing.TYPE_CHECKING:
    from typing import Any, Literal, Sequence

    import numpy.typing as npt
    import pandas as pd
    from matplotlib.axes import Axes
    from matplotlib.offsetbox import DrawingArea
    from matplotlib.path import Path

    from plotnine.coords.coord import coord
    from plotnine.iapi import panel_view
    from plotnine.layer import layer


@document
class geom_path(geom):
    """
    Connected points

    {usage}

    Parameters
    ----------
    {common_parameters}
    lineend : Literal["butt", "round", "projecting"], default="butt"
        Line end style. This option is applied for solid linetypes.
    linejoin : Literal["round", "miter", "bevel"], default="round"
        Line join style. This option is applied for solid linetypes.
    arrow : ~plotnine.geoms.geom_path.arrow, default=None
        Arrow specification. Default is no arrow.

    See Also
    --------
    plotnine.arrow : for adding arrowhead(s) to paths.
    """

    DEFAULT_AES = {
        "alpha": 1,
        "color": "black",
        "linetype": "solid",
        "size": 0.5,
    }

    REQUIRED_AES = {"x", "y"}
    DEFAULT_PARAMS = {
        "stat": "identity",
        "position": "identity",
        "na_rm": False,
        "lineend": "butt",
        "linejoin": "round",
        "arrow": None,
    }

    def handle_na(self, data: pd.DataFrame) -> pd.DataFrame:
        def keep(x: Sequence[float]) -> npt.NDArray[np.bool_]:
            # first non-missing to last non-missing
            first = match([False], x, nomatch=1, start=0)[0]
            last = len(x) - match([False], x[::-1], nomatch=1, start=0)[0]
            bool_idx = np.hstack(
                [
                    np.repeat(False, first),
                    np.repeat(True, last - first),
                    np.repeat(False, len(x) - last),
                ]
            )
            return bool_idx

        # Get indices where any row for the select aesthetics has
        # NaNs at the beginning or the end. Those we drop
        bool_idx = (
            data[["x", "y", "size", "color", "linetype"]]
            .isna()  # Missing
            .apply(keep, axis=0)
        )  # Beginning or the End
        bool_idx = np.all(bool_idx, axis=1)  # Across the aesthetics

        # return data
        n1 = len(data)
        data = data[bool_idx]
        data.reset_index(drop=True, inplace=True)
        n2 = len(data)

        if n2 != n1 and not self.params["na_rm"]:
            msg = "geom_path: Removed {} rows containing missing values."
            warn(msg.format(n1 - n2), PlotnineWarning)

        return data

    def draw_panel(
        self,
        data: pd.DataFrame,
        panel_params: panel_view,
        coord: coord,
        ax: Axes,
        **params: Any,
    ):
        if not any(data["group"].duplicated()):
            warn(
                "geom_path: Each group consist of only one "
                "observation. Do you need to adjust the "
                "group aesthetic?",
                PlotnineWarning,
            )

        # drop lines with less than two points
        c = Counter(data["group"])
        counts = np.array([c[v] for v in data["group"]])
        data = data[counts >= 2]

        if len(data) < 2:
            return

        # dataframe mergesort is stable, we rely on that here
        data = data.sort_values("group", kind="mergesort")
        data.reset_index(drop=True, inplace=True)

        # When the parameters of the path are not constant
        # with in the group, then the lines that make the paths
        # can be drawn as separate segments
        cols = {"color", "size", "linetype", "alpha", "group"}
        cols = cols & set(data.columns)
        num_unique_rows = len(data.drop_duplicates(cols))
        ngroup = len(np.unique(data["group"].to_numpy()))

        constant = num_unique_rows == ngroup
        params["constant"] = constant

        if not constant:
            self.draw_group(data, panel_params, coord, ax, **params)
        else:
            for _, gdata in data.groupby("group"):
                gdata.reset_index(inplace=True, drop=True)
                self.draw_group(gdata, panel_params, coord, ax, **params)

    @staticmethod
    def draw_group(
        data: pd.DataFrame,
        panel_params: panel_view,
        coord: coord,
        ax: Axes,
        **params: Any,
    ):
        data = coord.transform(data, panel_params, munch=True)
        data["linewidth"] = data["size"] * SIZE_FACTOR

        if "constant" in params:
            constant: bool = params.pop("constant")
        else:
            constant = len(np.unique(data["group"].to_numpy())) == 1

        if not constant:
            _draw_segments(data, ax, **params)
        else:
            _draw_lines(data, ax, **params)

        if "arrow" in params and params["arrow"]:
            params["arrow"].draw(
                data, panel_params, coord, ax, constant=constant, **params
            )

    @staticmethod
    def draw_legend(
        data: pd.Series[Any], da: DrawingArea, lyr: layer
    ) -> DrawingArea:
        """
        Draw a horizontal line in the box

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
        from matplotlib.lines import Line2D

        linewidth = data["size"] * SIZE_FACTOR
        x = [0, da.width]
        y = [0.5 * da.height] * 2
        color = to_rgba(data["color"], data["alpha"])

        key = Line2D(
            x,
            y,
            linestyle=data["linetype"],
            linewidth=linewidth,
            color=color,
            solid_capstyle="butt",
            antialiased=False,
        )
        da.add_artist(key)
        return da

    @staticmethod
    def legend_key_size(
        data: pd.Series[Any], min_size: tuple[int, int], lyr: layer
    ) -> tuple[int, int]:
        w, h = min_size
        pad_w, pad_h = w * 0.5, h * 0.5
        _w = _h = data.get("size", 0) * SIZE_FACTOR
        if data["color"] is not None:
            w = max(w, _w + pad_w)
            h = max(h, _h + pad_h)
        return w, h


class arrow:
    """
    Define arrow (actually an arrowhead)

    This is used to define arrow heads for
    [](`~plotnine.geoms.geom_path`).

    Parameters
    ----------
    angle :
        angle in degrees between the tail a
        single edge.
    length :
        of the edge in "inches"
    ends :
        At which end of the line to draw the
        arrowhead
    type :
        When it is closed, it is also filled
    """

    def __init__(
        self,
        angle: float = 30,
        length: float = 0.2,
        ends: Literal["first", "last", "both"] = "last",
        type: Literal["open", "closed"] = "open",
    ):
        self.angle = angle
        self.length = length
        self.ends = ends
        self.type = type

    def draw(
        self,
        data: pd.DataFrame,
        panel_params: panel_view,
        coord: coord,
        ax: Axes,
        constant: bool = True,
        **params: Any,
    ):
        """
        Draw arrows at the end(s) of the lines

        Parameters
        ----------
        data : dataframe
            Data to be plotted by this geom. This is the
            dataframe created in the plot_build pipeline.
        panel_params : panel_view
            The scale information as may be required by the
            axes. At this point, that information is about
            ranges, ticks and labels. Attributes are of interest
            to the geom are:

            ```python
            "panel_params.x.range"  # tuple
            "panel_params.y.range"  # tuple
            ```
        coord : coord
            Coordinate (e.g. coord_cartesian) system of the
            geom.
        ax : axes
            Axes on which to plot.
        constant: bool
            If the path attributes vary along the way. If false,
            the arrows are per segment of the path
        params : dict
            Combined parameters for the geom and stat. Also
            includes the `zorder`.
        """
        first = self.ends in ("first", "both")
        last = self.ends in ("last", "both")

        data = data.sort_values("group", kind="mergesort")
        data["color"] = to_rgba(data["color"], data["alpha"])

        if self.type == "open":
            data["facecolor"] = "none"
        else:
            data["facecolor"] = data["color"]

        if not constant:
            from matplotlib.collections import PathCollection

            # Get segments/points (x1, y1) -> (x2, y2)
            # for which to calculate the arrow heads
            idx1: list[int] = []
            idx2: list[int] = []
            for _, df in data.groupby("group"):
                idx1.extend(df.index[:-1].to_list())
                idx2.extend(df.index[1:].to_list())

            d = {
                "zorder": params["zorder"],
                "rasterized": params["raster"],
                "edgecolor": data.loc[idx1, "color"],
                "facecolor": data.loc[idx1, "facecolor"],
                "linewidth": data.loc[idx1, "linewidth"],
                "linestyle": data.loc[idx1, "linetype"],
            }

            x1 = data.loc[idx1, "x"].to_numpy()
            y1 = data.loc[idx1, "y"].to_numpy()
            x2 = data.loc[idx2, "x"].to_numpy()
            y2 = data.loc[idx2, "y"].to_numpy()

            if first:
                paths = self.get_paths(x1, y1, x2, y2, panel_params, coord, ax)
                coll = PathCollection(paths, **d)
                ax.add_collection(coll)
            if last:
                x1, y1, x2, y2 = x2, y2, x1, y1
                paths = self.get_paths(x1, y1, x2, y2, panel_params, coord, ax)
                coll = PathCollection(paths, **d)
                ax.add_collection(coll)
        else:
            from matplotlib.patches import PathPatch

            d = {
                "zorder": params["zorder"],
                "rasterized": params["raster"],
                "edgecolor": data["color"].iloc[0],
                "facecolor": data["facecolor"].iloc[0],
                "linewidth": data["linewidth"].iloc[0],
                "linestyle": data["linetype"].iloc[0],
                "joinstyle": "round",
                "capstyle": "butt",
            }

            if first:
                x1, x2 = data["x"].iloc[0:2]
                y1, y2 = data["y"].iloc[0:2]
                x1, y1, x2, y2 = (np.array([i]) for i in (x1, y1, x2, y2))
                paths = self.get_paths(x1, y1, x2, y2, panel_params, coord, ax)
                patch = PathPatch(paths[0], **d)
                ax.add_artist(patch)

            if last:
                x1, x2 = data["x"].iloc[-2:]
                y1, y2 = data["y"].iloc[-2:]
                x1, y1, x2, y2 = x2, y2, x1, y1
                x1, y1, x2, y2 = (np.array([i]) for i in (x1, y1, x2, y2))
                paths = self.get_paths(x1, y1, x2, y2, panel_params, coord, ax)
                patch = PathPatch(paths[0], **d)
                ax.add_artist(patch)

    def get_paths(
        self,
        x1: npt.ArrayLike,
        y1: npt.ArrayLike,
        x2: npt.ArrayLike,
        y2: npt.ArrayLike,
        panel_params: panel_view,
        coord: coord,
        ax: Axes,
    ) -> list[Path]:
        """
        Compute paths that create the arrow heads

        Parameters
        ----------
        x1, y1, x2, y2 : array_like
            List of points that define the tails of the arrows.
            The arrow heads will be at x1, y1. If you need them
            at x2, y2 reverse the input.
        panel_params : panel_view
            The scale information as may be required by the
            axes. At this point, that information is about
            ranges, ticks and labels. Attributes are of interest
            to the geom are:

            ```python
            "panel_params.x.range"  # tuple
            "panel_params.y.range"  # tuple
            ```
        coord : coord
            Coordinate (e.g. coord_cartesian) system of the geom.
        ax : axes
            Axes on which to plot.

        Returns
        -------
        out : list of Path
            Paths that create arrow heads
        """
        from matplotlib.path import Path

        # The arrowhead path has 3 vertices,
        # plus a dummy vertex for the STOP code
        dummy = (0, 0)

        # codes list remains the same after initialization
        codes = [Path.MOVETO, Path.LINETO, Path.LINETO, Path.STOP]

        # We need the axes dimensions so that we can
        # compute scaling factors
        width, height = _axes_get_size_inches(ax)
        ranges = coord.range(panel_params)
        width_ = np.ptp(ranges.x)
        height_ = np.ptp(ranges.y)

        # scaling factors to prevent skewed arrowheads
        lx = self.length * width_ / width
        ly = self.length * height_ / height

        # angle in radians
        a = self.angle * np.pi / 180

        # direction of arrow head
        xdiff, ydiff = x2 - x1, y2 - y1  # type: ignore
        rotations = np.arctan2(ydiff / ly, xdiff / lx)

        # Arrow head vertices
        v1x = x1 + lx * np.cos(rotations + a)
        v1y = y1 + ly * np.sin(rotations + a)
        v2x = x1 + lx * np.cos(rotations - a)
        v2y = y1 + ly * np.sin(rotations - a)

        # create a path for each arrow head
        paths = []
        for t in zip(v1x, v1y, x1, y1, v2x, v2y):  # type: ignore
            verts = [t[:2], t[2:4], t[4:], dummy]
            paths.append(Path(verts, codes))

        return paths


def _draw_segments(data: pd.DataFrame, ax: Axes, **params: Any):
    """
    Draw independent line segments between all the
    points
    """
    from matplotlib.collections import LineCollection

    color = to_rgba(data["color"], data["alpha"])
    # All we do is line-up all the points in a group
    # into segments, all in a single list.
    # Along the way the other parameters are put in
    # sequences accordingly
    indices: list[int] = []  # for attributes of starting point of each segment
    _segments = []
    for _, df in data.groupby("group"):
        idx = df.index
        indices.extend(idx[:-1].to_list())  # One line from two points
        x = data["x"].iloc[idx]
        y = data["y"].iloc[idx]
        _segments.append(make_line_segments(x, y, ispath=True))

    segments = np.vstack(_segments).tolist()

    edgecolor = color if color is None else [color[i] for i in indices]
    linewidth = data.loc[indices, "linewidth"]
    linestyle = data.loc[indices, "linetype"]

    coll = LineCollection(
        segments,
        edgecolor=edgecolor,
        linewidth=linewidth,
        linestyle=linestyle,
        capstyle=params.get("lineend"),
        zorder=params["zorder"],
        rasterized=params["raster"],
    )
    ax.add_collection(coll)


def _draw_lines(data: pd.DataFrame, ax: Axes, **params: Any):
    """
    Draw a path with the same characteristics from the
    first point to the last point
    """
    from matplotlib.lines import Line2D

    color = to_rgba(data["color"].iloc[0], data["alpha"].iloc[0])
    join_style = _get_joinstyle(data, params)
    lines = Line2D(
        data["x"],
        data["y"],
        color=color,
        linewidth=data["linewidth"].iloc[0],
        linestyle=data["linetype"].iloc[0],
        zorder=params["zorder"],
        rasterized=params["raster"],
        **join_style,
    )
    ax.add_artist(lines)


def _get_joinstyle(
    data: pd.DataFrame, params: dict[str, Any]
) -> dict[str, Any]:
    with suppress(KeyError):
        if params["linejoin"] == "mitre":
            params["linejoin"] = "miter"

    with suppress(KeyError):
        if params["lineend"] == "square":
            params["lineend"] = "projecting"

    joinstyle = params.get("linejoin", "miter")
    capstyle = params.get("lineend", "butt")
    d = {}
    if data["linetype"].iloc[0] == "solid":
        d["solid_joinstyle"] = joinstyle
        d["solid_capstyle"] = capstyle
    elif data["linetype"].iloc[0] == "dashed":
        d["dash_joinstyle"] = joinstyle
        d["dash_capstyle"] = capstyle
    return d


def _axes_get_size_inches(ax: Axes) -> tuple[float, float]:
    """
    Size of axes in inches

    Parameters
    ----------
    ax : axes
        Axes

    Returns
    -------
    out : tuple[float, float]
        (width, height) of ax in inches
    """
    fig = ax.get_figure()
    bbox = ax.get_window_extent().transformed(
        fig.dpi_scale_trans.inverted()  # pyright: ignore
    )
    return bbox.width, bbox.height

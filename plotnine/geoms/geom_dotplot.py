from __future__ import annotations

import typing
from warnings import warn

import narwhals as nw
import numpy as np

from .._utils import frame, groupby_apply, resolution, to_rgba
from ..doctools import document
from ..exceptions import PlotnineWarning
from .geom import geom
from .geom_path import geom_path

if typing.TYPE_CHECKING:
    from typing import Any

    from matplotlib.axes import Axes
    from matplotlib.offsetbox import DrawingArea

    from plotnine._utils.frame import DataFrame
    from plotnine.coords.coord import coord
    from plotnine.iapi import panel_view
    from plotnine.layer import layer
    from plotnine.typing import AnyArray


@document
class geom_dotplot(geom):
    """
    Dot plot

    {usage}

    Parameters
    ----------
    {common_parameters}
    stackdir : Literal["up", "down", "center", "centerwhole"], default="up"
        Direction in which to stack the dots. Options are
    stackratio : float, default=1
        How close to stack the dots. If value is less than 1,
        the dots overlap, if greater than 1 they are spaced.
    dotsize : float, default=1
        Diameter of dots relative to `binwidth`.
    stackgroups : bool, default=False
        If `True`{.py}, the dots are stacked across groups.

    See Also
    --------
    plotnine.stat_bindot : The default `stat` for this `geom`.
    """

    DEFAULT_AES = {"alpha": 1, "color": "black", "fill": "black"}
    REQUIRED_AES = {"x", "y"}
    NON_MISSING_AES = {"size", "shape"}
    DEFAULT_PARAMS = {
        "stat": "bindot",
        "stackdir": "up",
        "stackratio": 1,
        "dotsize": 1,
        "stackgroups": False,
    }

    legend_key_size = staticmethod(geom_path.legend_key_size)

    def setup_data(self, data: DataFrame) -> DataFrame:
        gp = self.params
        sp = self.params["stat_params"]

        # Issue warnings when parameters don't make sense
        if gp["position"] == "stack":
            warn(
                'position="stack" doesn"t work properly with '
                "geom_dotplot. Use stackgroups=True instead.",
                PlotnineWarning,
            )
        if (
            gp["stackgroups"]
            and sp["method"] == "dotdensity"
            and sp["binpositions"] == "bygroup"
        ):
            warn(
                "geom_dotplot called with stackgroups=TRUE and "
                'method="dotdensity". You probably want to set '
                'binpositions="all"',
                PlotnineWarning,
            )

        if "width" not in data.columns:
            if sp["width"]:
                width = sp["width"]
            else:
                width = resolution(data["x"], False) * 0.9
            data = frame.assign(data, width=width)

        # Set up the stacking function and range
        if gp["stackdir"] in (None, "up"):

            def stackdots(a: AnyArray) -> AnyArray:
                return a - 0.5

            stackaxismin: float = 0
            stackaxismax: float = 1
        elif gp["stackdir"] == "down":

            def stackdots(a: AnyArray) -> AnyArray:
                return -a + 0.5

            stackaxismin = -1
            stackaxismax = 0
        elif gp["stackdir"] == "center":

            def stackdots(a: AnyArray) -> AnyArray:
                return a - 1 - np.max(a - 1) / 2

            stackaxismin = -0.5
            stackaxismax = 0.5
        elif gp["stackdir"] == "centerwhole":

            def stackdots(a: AnyArray) -> AnyArray:
                return a - 1 - np.floor(np.max(a - 1) / 2)

            stackaxismin = -0.5
            stackaxismax = 0.5
        else:
            raise ValueError(f"Invalid value stackdir={gp['stackdir']}")

        # Fill the bins: at a given x (or y),
        # if count=3, make 3 entries at that x
        counts = data["count"].to_list()
        idx = [i for i, c in enumerate(counts) for j in range(int(c))]
        data = frame.take(data, idx)
        # Next part will set the position of each dot within each stack
        # If stackgroups=TRUE, split only on x (or y) and panel;
        # if not stacking, also split by group
        groupvars = [sp["binaxis"], "PANEL"]
        if not gp["stackgroups"]:
            groupvars.append("group")

        # Within each x, or x+group, set countidx=1,2,3,
        # and set stackpos according to stack function
        def func(df: DataFrame) -> DataFrame:
            countidx = np.arange(1, len(df) + 1)
            return frame.assign(
                df, countidx=countidx, stackpos=stackdots(countidx)
            )

        # Within each x, or x+group, set countidx=1,2,3, and set
        # stackpos according to stack function
        data = groupby_apply(data, groupvars, func)

        # Set the bounding boxes for the dots
        if sp["binaxis"] == "x":
            # ymin, ymax, xmin, and xmax define the bounding
            # rectangle for each stack. Can't do bounding box per dot,
            # because y position isn't real.
            # After position code is rewritten, each dot should have
            # its own bounding box.
            x, half_binwidth = nw.col("x"), nw.col("binwidth") / 2
            data = data.with_columns(
                xmin=x - half_binwidth,
                xmax=x + half_binwidth,
                ymin=nw.lit(stackaxismin),
                ymax=nw.lit(stackaxismax),
                y=nw.lit(0),
            )
        elif sp["binaxis"] == "y":
            # ymin, ymax, xmin, and xmax define the bounding
            # rectangle for each stack. Can't do bounding box per dot,
            # because x position isn't real.
            # xmin and xmax aren't really the x bounds. They're just
            # set to the standard x +- width/2 so that dot clusters
            # can be dodged like other geoms.
            # After position code is rewritten, each dot should have
            # its own bounding box.
            half_binwidth = data["binwidth"].item(0) / 2

            def func(df: DataFrame) -> DataFrame:
                y = nw.col("y")
                return df.with_columns(
                    ymin=y.min() - half_binwidth,
                    ymax=y.max() + half_binwidth,
                )

            data = groupby_apply(data, "group", func)
            x, width = nw.col("x"), nw.col("width")
            data = data.with_columns(
                xmin=x + width * stackaxismin,
                xmax=x + width * stackaxismax,
            )

        return data

    @staticmethod
    def draw_group(
        data: DataFrame,
        panel_params: panel_view,
        coord: coord,
        ax: Axes,
        params: dict[str, Any],
    ):
        from matplotlib.collections import PatchCollection
        from matplotlib.patches import Ellipse

        data = coord.transform(data, panel_params)
        fill = to_rgba(data["fill"], data["alpha"])
        color = to_rgba(data["color"], data["alpha"])
        ranges = coord.range(panel_params)

        # For perfect circles the width/height of the circle(ellipse)
        # should factor in the dimensions of axes
        bbox = ax.get_window_extent().transformed(
            ax.figure.dpi_scale_trans.inverted()
        )
        ax_width, ax_height = bbox.width, bbox.height

        factor = (ax_width / ax_height) * np.ptp(ranges.y) / np.ptp(ranges.x)
        size = data["binwidth"].item(0) * params["dotsize"]
        offsets = frame.to_numpy(data["stackpos"]) * params["stackratio"]
        x = frame.to_numpy(data["x"])
        y = frame.to_numpy(data["y"])

        binaxis = params["stat_params"]["binaxis"]
        if binaxis == "x":
            width, height = size, size * factor
            xpos, ypos = x, y + height * offsets
        elif binaxis == "y":
            width, height = size / factor, size
            xpos, ypos = x + width * offsets, y
        else:
            raise ValueError(f"Invalid valid value binaxis={binaxis}")

        circles = []
        for xy in zip(xpos, ypos):
            patch = Ellipse(xy, width=width, height=height)
            circles.append(patch)

        coll = PatchCollection(
            circles,
            edgecolors=color,
            facecolors=fill,
            rasterized=params["raster"],
        )
        ax.add_collection(coll)

    @staticmethod
    def draw_legend(
        data: dict[str, Any], da: DrawingArea, lyr: layer
    ) -> DrawingArea:
        """
        Draw a point in the box

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

        fill = to_rgba(data["fill"], data["alpha"])
        key = Line2D(
            [0.5 * da.width],
            [0.5 * da.height],
            marker="o",
            markersize=da.width / 2,
            markerfacecolor=fill,
            markeredgecolor=data["color"],
        )
        da.add_artist(key)
        return da

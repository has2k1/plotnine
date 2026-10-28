from __future__ import annotations

import typing
from warnings import warn

import narwhals as nw
import numpy as np

from .._utils import (
    SIZE_FACTOR,
    copy_missing_columns,
    frame,
    resolution,
    to_rgba,
)
from ..doctools import document
from ..exceptions import PlotnineWarning
from .geom import geom
from .geom_polygon import geom_polygon
from .geom_segment import geom_segment

if typing.TYPE_CHECKING:
    from typing import Any

    import numpy.typing as npt
    from matplotlib.axes import Axes
    from matplotlib.offsetbox import DrawingArea

    from plotnine._utils.frame import DataFrame
    from plotnine.coords.coord import coord
    from plotnine.iapi import panel_view
    from plotnine.layer import layer


@document
class geom_crossbar(geom):
    """
    Vertical interval represented by a crossbar

    {usage}

    Parameters
    ----------
    {common_parameters}
    width : float, default=0.5
        Box width as a fraction of the resolution of the data.
    fatten : float, default=2
        A multiplicative factor used to increase the size of the
        middle bar across the box.
    """

    DEFAULT_AES = {
        "alpha": 1,
        "color": "black",
        "fill": None,
        "linetype": "solid",
        "size": 0.5,
    }
    REQUIRED_AES = {"x", "y", "ymin", "ymax"}
    DEFAULT_PARAMS = {"width": 0.5, "fatten": 2}

    legend_key_size = staticmethod(geom_segment.legend_key_size)

    def setup_data(self, data: DataFrame) -> DataFrame:
        if "width" not in data.columns:
            if self.params["width"]:
                width = self.params["width"]
            else:
                width = resolution(data["x"], False) * 0.9
            data = frame.assign(data, width=width)

        x = nw.col("x")
        half_width = nw.col("width") / 2
        return data.with_columns(
            xmin=x - half_width, xmax=x + half_width
        ).drop("width")

    @staticmethod
    def draw_group(
        data: DataFrame,
        panel_params: panel_view,
        coord: coord,
        ax: Axes,
        params: dict[str, Any],
    ):
        y = frame.to_numpy(data["y"])
        xmin = frame.to_numpy(data["xmin"])
        xmax = frame.to_numpy(data["xmax"])
        ymin = frame.to_numpy(data["ymin"])
        ymax = frame.to_numpy(data["ymax"])
        group = frame.to_numpy(data["group"])

        # From violin
        notchwidth = typing.cast("float", params.get("notchwidth"))
        # ynotchupper = data.get('ynotchupper')
        # ynotchlower = data.get('ynotchlower')

        def flat(*args: npt.NDArray[Any]) -> npt.NDArray[Any]:
            """Flatten list-likes"""
            return np.hstack(args)

        middle = {"x": xmin, "y": y, "xend": xmax, "yend": y, "group": group}

        has_notch = (
            "ynotchupper" in data.columns and "ynotchlower" in data.columns
        )
        if has_notch:  # 10 points + 1 closing
            ynotchupper = frame.to_numpy(data["ynotchupper"])
            ynotchlower = frame.to_numpy(data["ynotchlower"])

            if any(ynotchlower < ymin) or any(ynotchupper > ymax):
                warn(
                    "Notch went outside the hinges. Try setting notch=False.",
                    PlotnineWarning,
                )

            notchindent = (1 - notchwidth) * (xmax - xmin) / 2

            middle["x"] = middle["x"] + notchindent
            middle["xend"] = middle["xend"] - notchindent
            box = {
                "x": flat(
                    xmin,
                    xmin,
                    xmin + notchindent,
                    xmin,
                    xmin,
                    xmax,
                    xmax,
                    xmax - notchindent,
                    xmax,
                    xmax,
                    xmin,
                ),
                "y": flat(
                    ymax,
                    ynotchupper,
                    y,
                    ynotchlower,
                    ymin,
                    ymin,
                    ynotchlower,
                    y,
                    ynotchupper,
                    ymax,
                    ymax,
                ),
                "group": np.tile(np.arange(1, len(group) + 1), 11),
            }
        else:
            # No notch, 4 points + 1 closing
            box = {
                "x": flat(xmin, xmin, xmax, xmax, xmin),
                "y": flat(ymax, ymax, ymax, ymin, ymin),
                "group": np.tile(np.arange(1, len(group) + 1), 5),
            }

        middle_data = copy_missing_columns(
            frame.frame_like(data, middle), data
        )
        middle_data = middle_data.with_columns(
            alpha=nw.lit(1), size=nw.col("size") * params["fatten"]
        )
        box_data = copy_missing_columns(frame.frame_like(data, box), data)
        geom_polygon.draw_group(box_data, panel_params, coord, ax, params)
        geom_segment.draw_group(middle_data, panel_params, coord, ax, params)

    @staticmethod
    def draw_legend(
        data: dict[str, Any], da: DrawingArea, lyr: layer
    ) -> DrawingArea:
        """
        Draw a rectangle with a horizontal strike in the box

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
        from matplotlib.patches import Rectangle

        linewidth = data["size"] * SIZE_FACTOR

        # background
        facecolor = to_rgba(data["fill"], data["alpha"])
        if facecolor is None:
            facecolor = "none"

        bg = Rectangle(
            (da.width * 0.125, da.height * 0.25),
            width=da.width * 0.75,
            height=da.height * 0.5,
            linewidth=linewidth,
            facecolor=facecolor,
            edgecolor=data["color"],
            linestyle=data["linetype"],
            capstyle="projecting",
            antialiased=False,
        )
        da.add_artist(bg)

        strike = Line2D(
            [da.width * 0.125, da.width * 0.875],
            [da.height * 0.5, da.height * 0.5],
            linestyle=data["linetype"],
            linewidth=linewidth,
            color=data["color"],
        )
        da.add_artist(strike)
        return da

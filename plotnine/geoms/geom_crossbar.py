from __future__ import annotations

import typing
from warnings import warn

import numpy as np
import pandas as pd

from .._utils import SIZE_FACTOR, copy_missing_columns, resolution, to_rgba
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
    DEFAULT_PARAMS = {
        "stat": "identity",
        "position": "identity",
        "na_rm": False,
        "width": 0.5,
        "fatten": 2,
    }

    legend_key_size = staticmethod(geom_segment.legend_key_size)

    def setup_data(self, data: pd.DataFrame) -> pd.DataFrame:
        if "width" not in data:
            if self.params["width"]:
                data["width"] = self.params["width"]
            else:
                data["width"] = resolution(data["x"], False) * 0.9

        data["xmin"] = data["x"] - data["width"] / 2
        data["xmax"] = data["x"] + data["width"] / 2
        del data["width"]
        return data

    @staticmethod
    def draw_group(
        data: pd.DataFrame,
        panel_params: panel_view,
        coord: coord,
        ax: Axes,
        **params: Any,
    ):
        y = data["y"]
        xmin = data["xmin"]
        xmax = data["xmax"]
        ymin = data["ymin"]
        ymax = data["ymax"]
        group = data["group"]

        # From violin
        notchwidth = typing.cast(float, params.get("notchwidth"))
        # ynotchupper = data.get('ynotchupper')
        # ynotchlower = data.get('ynotchlower')

        def flat(*args: pd.Series[Any]) -> npt.NDArray[Any]:
            """Flatten list-likes"""
            return np.hstack(args)

        middle = pd.DataFrame(
            {"x": xmin, "y": y, "xend": xmax, "yend": y, "group": group}
        )
        copy_missing_columns(middle, data)
        middle["alpha"] = 1
        middle["size"] *= params["fatten"]

        has_notch = "ynotchupper" in data and "ynotchlower" in data
        if has_notch:  # 10 points + 1 closing
            ynotchupper = data["ynotchupper"]
            ynotchlower = data["ynotchlower"]

            if any(ynotchlower < ymin) or any(ynotchupper > ymax):
                warn(
                    "Notch went outside the hinges. "
                    "Try setting notch=False.",
                    PlotnineWarning,
                )

            notchindent = (1 - notchwidth) * (xmax - xmin) / 2

            middle["x"] += notchindent
            middle["xend"] -= notchindent
            box = pd.DataFrame(
                {
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
            )
        else:
            # No notch, 4 points + 1 closing
            box = pd.DataFrame(
                {
                    "x": flat(xmin, xmin, xmax, xmax, xmin),
                    "y": flat(ymax, ymax, ymax, ymin, ymin),
                    "group": np.tile(np.arange(1, len(group) + 1), 5),
                }
            )

        copy_missing_columns(box, data)
        geom_polygon.draw_group(box, panel_params, coord, ax, **params)
        geom_segment.draw_group(middle, panel_params, coord, ax, **params)

    @staticmethod
    def draw_legend(
        data: pd.Series[Any], da: DrawingArea, lyr: layer
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

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
from ..positions import position_dodge2
from ..positions.position import position
from .geom import geom
from .geom_crossbar import geom_crossbar
from .geom_point import geom_point
from .geom_segment import geom_segment

if typing.TYPE_CHECKING:
    from typing import Any

    import numpy.typing as npt
    from matplotlib.axes import Axes
    from matplotlib.offsetbox import DrawingArea

    from plotnine import aes
    from plotnine._utils.frame import DataFrame
    from plotnine.coords.coord import coord
    from plotnine.iapi import panel_view
    from plotnine.layer import layer
    from plotnine.typing import DataLike


@document
class geom_boxplot(geom):
    """
    Box and whiskers plot

    {usage}

    Parameters
    ----------
    {common_parameters}
    width : float, default=None
        Box width. If `None`{.py}, the width is set to
        `90%` of the resolution of the data. Note that if the stat
        has a width parameter, that takes precedence over this one.
    outlier_alpha : float, default=1
        Transparency of the outlier points.
    outlier_color : str | tuple, default=None
        Color of the outlier points.
    outlier_shape : str, default="o"
        Shape of the outlier points. An empty string hides the outliers.
    outlier_size : float, default=1.5
        Size of the outlier points.
    outlier_stroke : float, default=0.5
        Stroke-size of the outlier points.
    notch : bool, default=False
        Whether the boxes should have a notch.
    varwidth : bool, default=False
        If `True`{.py}, boxes are drawn with widths proportional to
        the square-roots of the number of observations in the
        groups.
    notchwidth : float, default=0.5
        Width of notch relative to the body width.
    fatten : float, default=2
        A multiplicative factor used to increase the size of the
        middle bar across the box.

    See Also
    --------
    plotnine.stat_boxplot : The default `stat` for this `geom`.
    """

    DEFAULT_AES = {
        "alpha": 1,
        "color": "#333333",
        "fill": "white",
        "linetype": "solid",
        "shape": "o",
        "size": 0.5,
        "weight": 1,
    }
    REQUIRED_AES = {"x", "lower", "upper", "middle", "ymin", "ymax"}
    DEFAULT_PARAMS = {
        "stat": "boxplot",
        "position": "dodge2",
        "width": None,
        "outlier_alpha": 1,
        "outlier_color": None,
        "outlier_shape": "o",
        "outlier_size": 1.5,
        "outlier_stroke": 0.5,
        "notch": False,
        "varwidth": False,
        "notchwidth": 0.5,
        "fatten": 2,
    }

    legend_key_size = staticmethod(geom_crossbar.legend_key_size)

    def __init__(
        self,
        mapping: aes | None = None,
        data: DataLike | None = None,
        **kwargs: Any,
    ):
        _position = kwargs.get("position", self.DEFAULT_PARAMS["position"])
        varwidth = kwargs.get("varwidth", self.DEFAULT_PARAMS["varwidth"])

        # varwidth = True is not compatible with preserve="total"
        if varwidth:
            if isinstance(_position, str):
                kwargs["position"] = position_dodge2(preserve="single")
            elif (
                isinstance(_position, position)
                and _position.params["preserve"] == "total"
            ):
                warn(
                    "Cannot preserve total widths when varwidth=True",
                    PlotnineWarning,
                    stacklevel=2,
                )
                _position.params["preserve"] = "single"

        super().__init__(mapping, data, **kwargs)

    def setup_data(self, data: DataFrame) -> DataFrame:
        if "width" not in data.columns:
            width = self.params.get("width", None)
            if width is None:
                width = resolution(data["x"], False) * 0.9
            data = frame.assign(data, width=width)

        if "outliers" not in data.columns or self.params["outlier_shape"] in (
            None,
            "",
        ):
            data = frame.assign(
                data,
                outliers=frame.series(
                    [[] for i in range(len(data))],
                    backend=data.implementation,
                    dtype=nw.Object,
                ),
            )

        # min and max outlier values
        outliers = data["outliers"].to_list()
        omin = [np.min(lst) if len(lst) else +np.inf for lst in outliers]
        omax = [np.max(lst) if len(lst) else -np.inf for lst in outliers]

        ymin = frame.to_numpy(data["ymin"])
        ymax = frame.to_numpy(data["ymax"])
        x = frame.to_numpy(data["x"])
        width = frame.to_numpy(data["width"])
        data = frame.assign(
            data,
            ymin_final=np.min(np.column_stack([ymin, omin]), axis=1),
            ymax_final=np.max(np.column_stack([ymax, omax]), axis=1),
        )

        # if varwidth not requested or not available, don't use it
        if (
            "varwidth" not in self.params
            or not self.params["varwidth"]
            or "relvarwidth" not in data.columns
        ):
            half_width = width / 2
        else:
            # make relvarwidth relative to the size of the
            # largest group
            relvarwidth = frame.to_numpy(data["relvarwidth"])
            relvarwidth = relvarwidth / relvarwidth.max()
            half_width = relvarwidth * width / 2
            data = data.drop("relvarwidth")

        data = frame.assign(data, xmin=x - half_width, xmax=x + half_width)
        return data.drop("width")

    @staticmethod
    def draw_group(
        data: DataFrame,
        panel_params: panel_view,
        coord: coord,
        ax: Axes,
        params: dict[str, Any],
    ):
        def flat(*columns: str) -> npt.NDArray[Any]:
            """Flatten list-likes"""
            return np.hstack([frame.to_numpy(data[c]) for c in columns])

        common_columns = [
            "color",
            "size",
            "linetype",
            "fill",
            "group",
            "alpha",
            "shape",
        ]
        # whiskers
        whiskers = frame.frame_like(
            data,
            {
                "x": flat("x", "x"),
                "y": flat("upper", "lower"),
                "yend": flat("ymax", "ymin"),
                "alpha": 1,
            },
        )
        whiskers = whiskers.with_columns(xend=nw.col("x"))
        whiskers = copy_missing_columns(whiskers, data.select(common_columns))

        # box
        box_columns = ["xmin", "xmax", "lower", "middle", "upper"]
        box = data.select(common_columns + box_columns).rename(
            {"lower": "ymin", "middle": "y", "upper": "ymax"}
        )

        # notch
        if params["notch"]:
            box = box.with_columns(
                data["notchlower"].alias("ynotchlower"),
                data["notchupper"].alias("ynotchupper"),
            )

        # outliers
        outliers = data["outliers"].item(0)
        num_outliers = len(outliers)
        if num_outliers:

            def outlier_value(param: str) -> Any:
                oparam = f"outlier_{param}"
                if params[oparam] is not None:
                    return params[oparam]
                return data[param].item(0)

            outliers_data = frame.frame_like(
                data,
                {
                    "y": np.asarray(outliers, dtype=float),
                    "x": np.repeat(data["x"].item(0), num_outliers),
                    "fill": [None] * num_outliers,
                    "alpha": outlier_value("alpha"),
                    "color": outlier_value("color"),
                    "shape": outlier_value("shape"),
                    "size": outlier_value("size"),
                    "stroke": outlier_value("stroke"),
                },
            )
            geom_point.draw_group(
                outliers_data, panel_params, coord, ax, params
            )

        # plot
        geom_segment.draw_group(whiskers, panel_params, coord, ax, params)
        geom_crossbar.draw_group(box, panel_params, coord, ax, params)

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
        from matplotlib.lines import Line2D
        from matplotlib.patches import Rectangle

        # box
        facecolor = to_rgba(data["fill"], data["alpha"])
        if facecolor is None:
            facecolor = "none"

        kwargs = {"linestyle": data["linetype"]}

        box = Rectangle(
            (da.width * 0.125, da.height * 0.25),
            width=da.width * 0.75,
            height=da.height * 0.5,
            facecolor=facecolor,
            edgecolor=data["color"],
            linewidth=data["size"],
            capstyle="projecting",
            antialiased=False,
            **kwargs,
        )
        da.add_artist(box)

        kwargs["solid_capstyle"] = "butt"
        kwargs["color"] = data["color"]
        kwargs["linewidth"] = data["size"] * SIZE_FACTOR

        # middle strike through
        strike = Line2D(
            [da.width * 0.125, da.width * 0.875],
            [da.height * 0.5, da.height * 0.5],
            **kwargs,
        )
        da.add_artist(strike)

        # whiskers
        top = Line2D(
            [da.width * 0.5, da.width * 0.5],
            [da.height * 0.75, da.height * 0.9],
            **kwargs,
        )
        da.add_artist(top)

        bottom = Line2D(
            [da.width * 0.5, da.width * 0.5],
            [da.height * 0.25, da.height * 0.1],
            **kwargs,
        )
        da.add_artist(bottom)
        return da

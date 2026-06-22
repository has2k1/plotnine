from __future__ import annotations

import typing
from copy import copy

import numpy as np

from .._utils import OPPOSITE_SIDE
from ..iapi import panel_ranges

if typing.TYPE_CHECKING:
    from typing import Any

    import numpy.typing as npt
    import pandas as pd
    from matplotlib.axes import Axes

    from plotnine import ggplot
    from plotnine.iapi import labels_view, layout_details, panel_view
    from plotnine.scales.scale import scale
    from plotnine.scales.scale_xy import ScaleX, ScaleY
    from plotnine.typing import (
        FloatArray,
        FloatArrayLike,
        FloatSeries,
        Side,
    )


def _activate_axis(axis, active_side: Side, present: bool):
    """
    Show ticks and labels on the active side only; hide the opposite side

    `present` is False on interior facet panels, which hides both sides.
    """
    opposite = OPPOSITE_SIDE[active_side]
    axis.set_tick_params(
        which="both",
        **{
            active_side: present,
            f"label{active_side}": present,
            opposite: False,
            f"label{opposite}": False,
        },
    )


class coord:
    """
    Base class for all coordinate systems
    """

    # If the coordinate system is linear
    is_linear = False

    # Additional parameters created acc. to the data,
    # if the coordinate system needs them
    params: dict[str, Any]

    def __radd__(self, other: ggplot) -> ggplot:
        """
        Add coordinates to ggplot object
        """
        other.coordinates = copy(self)
        return other

    def setup_data(self, data: list[pd.DataFrame]) -> list[pd.DataFrame]:
        """
        Allow the coordinate system to manipulate the layer data

        Parameters
        ----------
        data :
            Data for all Layer

        Returns
        -------
        :
            Modified layer data
        """
        return data

    def setup_params(self, data: list[pd.DataFrame]):
        """
        Create additional parameters

        A coordinate system may need to create parameters
        depending on the *original* data that the layers get.

        Parameters
        ----------
        data :
            Data for each layer before it is manipulated in
            any way.
        """
        self.params = {}

    def setup_layout(self, layout: pd.DataFrame) -> pd.DataFrame:
        """
        Allow the coordinate system alter the layout dataframe

        Parameters
        ----------
        layout :
            Dataframe in which data is assigned to panels and scales

        Returns
        -------
        :
            layout dataframe altered to according to the requirements
            of the coordinate system.

        Notes
        -----
        The input dataframe may be changed.
        """
        return layout

    def aspect(self, panel_params: panel_view) -> float | None:
        """
        Return desired aspect ratio for the plot

        If not overridden by the subclass, this method
        returns `None`, which means that the coordinate
        system does not influence the aspect ratio.
        """
        return None

    def setup_ax(
        self,
        ax: Axes,
        panel_params: panel_view,
        layout_info: layout_details,
    ) -> None:
        """
        Axes state for one panel: limits, breaks, labels, and active side

        Subclasses can override this or call `super().setup_ax(...)` and add
        coordinate-specific behavior. Configures only mpl axes state; the
        theme styles the visible artists afterwards.
        """
        self._setup_ticks_labels(ax, panel_params)
        self._setup_axis_sides(ax, panel_params, layout_info)

    def _setup_ticks_labels(self, ax: Axes, panel_params: panel_view) -> None:
        """
        Limits, major/minor breaks, tick labels, and fixed formatter on `ax`
        """
        from .._mpl.ticker import MyFixedFormatter

        def _inf_to_none(
            t: tuple[float, float],
        ) -> tuple[float | None, float | None]:
            """
            Replace infinities with None
            """
            a = t[0] if np.isfinite(t[0]) else None
            b = t[1] if np.isfinite(t[1]) else None
            return (a, b)

        # limits
        ax.set_xlim(*_inf_to_none(panel_params.x.range))
        ax.set_ylim(*_inf_to_none(panel_params.y.range))

        # breaks, labels
        ax.set_xticks(panel_params.x.breaks, panel_params.x.labels)
        ax.set_yticks(panel_params.y.breaks, panel_params.y.labels)

        # minor breaks
        ax.set_xticks(panel_params.x.minor_breaks, minor=True)
        ax.set_yticks(panel_params.y.minor_breaks, minor=True)

        # When you manually set the tick labels MPL changes the locator
        # so that it no longer reports the x & y positions
        # Fixes https://github.com/has2k1/plotnine/issues/187
        ax.xaxis.set_major_formatter(MyFixedFormatter(panel_params.x.labels))
        ax.yaxis.set_major_formatter(MyFixedFormatter(panel_params.y.labels))

    def _setup_axis_sides(
        self,
        ax: Axes,
        panel_params: panel_view,
        layout_info: layout_details,
    ) -> None:
        """
        Tick visibility and spine visibility for the side each axis occupies
        """
        x_pos = panel_params.x.position  # "bottom" | "top"
        y_pos = panel_params.y.position  # "left" | "right"
        _activate_axis(ax.xaxis, x_pos, layout_info.axis_x)
        _activate_axis(ax.yaxis, y_pos, layout_info.axis_y)

        # Spine on each axis's active side, on every panel (edge or
        # interior); the axis_line themeable styles or blanks it.
        ax.spines["top"].set_visible(x_pos == "top")
        ax.spines["bottom"].set_visible(x_pos == "bottom")
        ax.spines["right"].set_visible(y_pos == "right")
        ax.spines["left"].set_visible(y_pos == "left")

    def labels(self, cur_labels: labels_view) -> labels_view:
        """
        Modify labels

        Parameters
        ----------
        cur_labels :
            Current labels. The coord can modify them as necessary.

        Returns
        -------
        :
            Modified labels. Same object as the input.
        """
        return cur_labels

    def transform(
        self, data: pd.DataFrame, panel_params: panel_view, munch: bool = False
    ) -> pd.DataFrame:
        """
        Transform data before it is plotted

        This is used to "transform the coordinate axes".
        Subclasses should override this method
        """
        return data

    def setup_panel_params(
        self, scale_x: ScaleX, scale_y: ScaleY
    ) -> panel_view:
        """
        Compute the range and break information for the panel
        """
        msg = "The coordinate should implement this method."
        raise NotImplementedError(msg)

    def range(self, panel_params: panel_view) -> panel_ranges:
        """
        Return the range along the dimensions of the coordinate system
        """
        # Defaults to providing the 2D x-y ranges
        return panel_ranges(x=panel_params.x.range, y=panel_params.y.range)

    def backtransform_range(self, panel_params: panel_view) -> panel_ranges:
        """
        Backtransform the panel range in panel_params to data coordinates

        Coordinate systems that do any transformations should override
        this method. e.g. coord_trans has to override this method.
        """
        return self.range(panel_params)

    def distance(
        self,
        x: FloatSeries,
        y: FloatSeries,
        panel_params: panel_view,
    ) -> npt.NDArray[Any]:
        msg = "The coordinate should implement this method."
        raise NotImplementedError(msg)

    def munch(
        self, data: pd.DataFrame, panel_params: panel_view
    ) -> pd.DataFrame:
        ranges = self.backtransform_range(panel_params)

        x_neginf = np.isneginf(data["x"])
        x_posinf = np.isposinf(data["x"])
        y_neginf = np.isneginf(data["y"])
        y_posinf = np.isposinf(data["y"])
        if x_neginf.any():
            data.loc[x_neginf, "x"] = ranges.x[0]
        if x_posinf.any():
            data.loc[x_posinf, "x"] = ranges.x[1]
        if y_neginf.any():
            data.loc[y_neginf, "y"] = ranges.y[0]
        if y_posinf.any():
            data.loc[y_posinf, "y"] = ranges.y[1]

        dist = self.distance(data["x"], data["y"], panel_params)
        bool_idx = (
            data["group"].to_numpy()[1:] != data["group"].to_numpy()[:-1]
        )
        dist[bool_idx] = np.nan

        # Munch
        munched = munch_data(data, dist)
        return munched


def dist_euclidean(x: FloatArrayLike, y: FloatArrayLike) -> FloatArray:
    """
    Calculate euclidean distance
    """
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    return np.sqrt(
        (x[:-1] - x[1:]) ** 2 + (y[:-1] - y[1:]) ** 2, dtype=np.float64
    )


def interp(start: int, end: int, n: int) -> FloatArray:
    """
    Interpolate
    """
    return np.linspace(start, end, n, endpoint=False)


def munch_data(data: pd.DataFrame, dist: FloatArray) -> pd.DataFrame:
    """
    Breakup path into small segments
    """
    x, y = data["x"], data["y"]
    segment_length = 0.01

    # How many endpoints for each old segment,
    # not counting the last one
    dist[np.isnan(dist)] = 1
    extra = np.maximum(np.floor(dist / segment_length), 1)
    extra = extra.astype(int)

    # Generate extra pieces for x and y values
    # The final point must be manually inserted at the end
    x = [interp(start, end, n) for start, end, n in zip(x[:-1], x[1:], extra)]
    y = [interp(start, end, n) for start, end, n in zip(y[:-1], y[1:], extra)]
    x.append(data["x"].iloc[-1])
    y.append(data["y"].iloc[-1])
    x = np.hstack(x)
    y = np.hstack(y)

    # Replicate other aesthetics: defined by start point
    # but also must include final point
    idx = np.hstack(
        [
            np.repeat(data.index[:-1], extra),
            len(data) - 1,
            # data.index[-1] # TODO: Maybe not
        ]
    )

    munched = data.loc[idx, list(data.columns.difference(["x", "y"]))]
    munched["x"] = x
    munched["y"] = y
    munched.reset_index(drop=True, inplace=True)

    return munched

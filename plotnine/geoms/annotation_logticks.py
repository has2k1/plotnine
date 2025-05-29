from __future__ import annotations

import typing
import warnings

import numpy as np
import pandas as pd

from .._utils import log
from ..coords import coord_flip
from ..exceptions import PlotnineWarning
from ..scales.scale_continuous import scale_continuous as ScaleContinuous
from .annotate import annotate
from .geom_path import geom_path
from .geom_rug import geom_rug

if typing.TYPE_CHECKING:
    from typing import Any, Literal, Optional, Sequence

    from matplotlib.axes import Axes

    from plotnine.coords.coord import coord
    from plotnine.facets.layout import Layout
    from plotnine.geoms.geom import geom
    from plotnine.iapi import panel_view
    from plotnine.typing import AnyArray


class _geom_logticks(geom_rug):
    """
    Internal geom implementing drawing of annotation_logticks
    """

    DEFAULT_AES = {}
    DEFAULT_PARAMS = {
        "stat": "identity",
        "position": "identity",
        "na_rm": False,
        "sides": "bl",
        "alpha": 1,
        "color": "black",
        "size": 0.5,
        "linetype": "solid",
        "lengths": (0.036, 0.0225, 0.012),
        "base": 10,
    }
    draw_legend = staticmethod(geom_path.draw_legend)

    def draw_layer(self, data: pd.DataFrame, layout: Layout, coord: coord):
        """
        Draw ticks on every panel
        """
        for pid in layout.layout["PANEL"]:
            ploc = pid - 1
            panel_params = layout.panel_params[ploc]
            ax = layout.axs[ploc]
            self.draw_panel(data, panel_params, coord, ax)

    @staticmethod
    def _check_log_scale(
        base: Optional[float],
        sides: str,
        panel_params: panel_view,
        coord: coord,
    ) -> tuple[float, float]:
        """
        Check the log transforms

        Parameters
        ----------
        base : float | None
            Base of the logarithm in which the ticks will be
            calculated. If `None`, the base of the log transform
            the scale will be used.
        sides : str, default="bl"
            Sides onto which to draw the marks. Any combination
            chosen from the characters `btlr`, for *bottom*, *top*,
            *left* or *right* side marks. If `coord_flip()` is used,
            these are the sides *before* the flip.
        panel_params : panel_view
            `x` and `y` view scale values.
        coord : coord
            Coordinate (e.g. coord_cartesian) system of the geom.

        Returns
        -------
        out : tuple
            The bases (base_x, base_y) to use when generating the ticks.
        """

        def get_base(sc, ubase: Optional[float]) -> float:
            ae = sc.aesthetics[0]

            if not isinstance(sc, ScaleContinuous) or not sc.is_log_scale:
                warnings.warn(
                    f"annotation_logticks for {ae}-axis which does not have "
                    "a log scale. The logticks may not make sense.",
                    PlotnineWarning,
                )
                return 10 if ubase is None else ubase

            base = sc._trans.base  # pyright: ignore
            if ubase is not None and base != ubase:
                warnings.warn(
                    f"The x-axis is log transformed in base={base} ,"
                    "but the annotation_logticks are computed in base="
                    f"{ubase}",
                    PlotnineWarning,
                )
                return ubase
            return base

        base_x, base_y = 10, 10
        x_scale = panel_params.x.scale
        y_scale = panel_params.y.scale

        if isinstance(coord, coord_flip):
            x_scale, y_scale = y_scale, x_scale
            base_x, base_y = base_y, base_x

        if "t" in sides or "b" in sides:
            base_x = get_base(x_scale, base)

        if "l" in sides or "r" in sides:
            base_y = get_base(y_scale, base)

        return base_x, base_y

    @staticmethod
    def _calc_ticks(
        value_range: tuple[float, float], base: float
    ) -> tuple[AnyArray, AnyArray, AnyArray]:
        """
        Calculate tick marks within a range

        Parameters
        ----------
        value_range: tuple
            Range for which to calculate ticks.

        base : number
            Base of logarithm

        Returns
        -------
        out: tuple
            (major, middle, minor) tick locations
        """

        def _minor(x: Sequence[Any], mid_idx: int) -> AnyArray:
            return np.hstack([x[1:mid_idx], x[mid_idx + 1 : -1]])

        # * Calculate the low and high powers,
        # * Generate for all intervals in along the low-high power range
        #   The intervals are in normal space
        # * Calculate evenly spaced breaks in normal space, then convert
        #   them to log space.
        low = np.floor(value_range[0])
        high = np.ceil(value_range[1])
        arr = base ** np.arange(low, float(high + 1))
        n_ticks = int(np.round(base) - 1)
        breaks = [
            log(np.linspace(b1, b2, n_ticks + 1), base)
            for (b1, b2) in list(zip(arr, arr[1:]))
        ]

        # Partition the breaks in the 3 groups
        major = np.array([x[0] for x in breaks] + [breaks[-1][-1]])
        if n_ticks % 2:
            mid_idx = n_ticks // 2
            middle = np.array([x[mid_idx] for x in breaks])
            minor = np.hstack([_minor(x, mid_idx) for x in breaks])
        else:
            middle = np.array([])
            minor = np.hstack([x[1:-1] for x in breaks])

        return major, middle, minor

    def draw_panel(
        self,
        data: pd.DataFrame,
        panel_params: panel_view,
        coord: coord,
        ax: Axes,
    ):
        params = self.params
        # Any passed data is ignored, the relevant data is created
        sides = params["sides"]
        lengths = params["lengths"]
        _aesthetics = {
            "size": params["size"],
            "color": params["color"],
            "alpha": params["alpha"],
            "linetype": params["linetype"],
        }

        def _draw(
            geom: geom,
            axis: Literal["x", "y"],
            tick_positions: tuple[AnyArray, AnyArray, AnyArray],
        ):
            for position, length in zip(tick_positions, lengths):
                data = pd.DataFrame({axis: position, **_aesthetics})
                params["length"] = length
                geom.draw_group(data, panel_params, coord, ax, params)

        if isinstance(coord, coord_flip):
            tick_range_x = panel_params.y.range
            tick_range_y = panel_params.x.range
        else:
            tick_range_x = panel_params.x.range
            tick_range_y = panel_params.y.range

        # these are already flipped iff coord_flip
        base_x, base_y = self._check_log_scale(
            params["base"], sides, panel_params, coord
        )

        if "b" in sides or "t" in sides:
            tick_positions = self._calc_ticks(tick_range_x, base_x)
            _draw(self, "x", tick_positions)

        if "l" in sides or "r" in sides:
            tick_positions = self._calc_ticks(tick_range_y, base_y)
            _draw(self, "y", tick_positions)


class annotation_logticks(annotate):
    """
    Marginal log ticks.

    If added to a plot that does not have a log10 axis
    on the respective side, a warning will be issued.

    Parameters
    ----------
    sides :
        Sides onto which to draw the marks. Any combination
        chosen from the characters `btlr`, for *bottom*, *top*,
        *left* or *right* side marks. If `coord_flip()` is used,
        these are the sides *after* the flip.
    alpha :
        Transparency of the ticks
    color :
        Colour of the ticks
    size :
        Thickness of the ticks
    linetype :
        Type of line
    lengths:
        length of the ticks drawn for full / half / tenth
        ticks relative to panel size
    base :
        Base of the logarithm in which the ticks will be
        calculated. If `None`, the base used to log transform
        the scale will be used.
    """

    def __init__(
        self,
        sides: str = "bl",
        alpha: float = 1,
        color: str
        | tuple[float, float, float]
        | tuple[float, float, float, float] = "black",
        size: float = 0.5,
        linetype: Literal["solid", "dashed", "dashdot", "dotted"]
        | Sequence[float] = "solid",
        lengths: tuple[float, float, float] = (0.036, 0.0225, 0.012),
        base: float | None = None,
    ):
        if len(lengths) != 3:
            raise ValueError(
                "length for annotation_logticks must be a tuple of 3 floats"
            )

        self._annotation_geom = _geom_logticks(
            sides=sides,
            alpha=alpha,
            color=color,
            size=size,
            linetype=linetype,
            lengths=lengths,
            base=base,
            inherit_aes=False,
            show_legend=False,
        )

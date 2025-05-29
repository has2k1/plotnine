from __future__ import annotations

import typing
from itertools import cycle, islice

import numpy as np
import pandas as pd

from ..coords import coord_flip
from ..scales.scale_discrete import scale_discrete
from .annotate import annotate
from .geom import geom
from .geom_polygon import geom_polygon
from .geom_rect import geom_rect

if typing.TYPE_CHECKING:
    from typing import Any, Literal, Sequence

    from matplotlib.axes import Axes

    from plotnine.coords.coord import coord
    from plotnine.facets.layout import Layout
    from plotnine.iapi import panel_view


class annotation_stripes(annotate):
    """
    Alternating stripes, centered around each label.

    Useful as a background for geom_jitter.

    Parameters
    ----------
    fill :
        List of colors for the strips.
    fill_range :
        How to fill stripes beyond the range of scale:

        ```python
        "cycle"      # keep cycling the colors of the
                     # stripes after the range ends
        "nocycle"    # stop cycling the colors of the
                     # stripes after the range ends
        "auto"       # "cycle" for continuous scales and
                     # "nocycle" for discrete scales.
        "no"         # Do not add stripes passed the range
                     # passed the range of the scales
        ```
    direction :
        Orientation of the stripes
    extend :
        Range of the stripes. The default is (0, 1), top to bottom.
        The values should be in the range [0, 1].
    **kwargs :
        Other aesthetic parameters for the rectangular stripes.
        They include; `alpha`, `color`, `linetype`, and `size`.
    """

    def __init__(
        self,
        fill: Sequence[str] = ("#AAAAAA", "#CCCCCC"),
        fill_range: Literal["auto", "cycle", "no", "nocycle"] = "auto",
        direction: Literal["horizontal", "vertical"] = "vertical",
        extend: tuple[float, float] = (0, 1),
        **kwargs: Any,
    ):
        allowed = ("vertical", "horizontal")
        if direction not in allowed:
            raise ValueError(f"direction must be one of {allowed}")
        self._annotation_geom = _geom_stripes(
            fill=fill,
            fill_range=fill_range,
            extend=extend,
            direction=direction,
            inherit_aes=False,
            show_legend=False,
            **kwargs,
        )


class _geom_stripes(geom):
    DEFAULT_AES = {}
    REQUIRED_AES = set()
    DEFAULT_PARAMS = {
        "stat": "identity",
        "position": "identity",
        "na_rm": False,
        "color": None,
        "fill": ("#AAAAAA", "#CCCCCC"),
        "linetype": "solid",
        "size": 1,
        "alpha": 0.5,
        "direction": "vertical",
        "extend": (0, 1),
        "fill_range": "auto",
    }
    draw_legend = staticmethod(geom_polygon.draw_legend)

    def draw_layer(self, data: pd.DataFrame, layout: Layout, coord: coord):
        """
        Draw stripes on every panel
        """
        for pid in layout.layout["PANEL"]:
            ploc = pid - 1
            panel_params = layout.panel_params[ploc]
            ax = layout.axs[ploc]
            self.draw_group(data, panel_params, coord, ax, self.params)

    @staticmethod
    def draw_group(
        data: pd.DataFrame,
        panel_params: panel_view,
        coord: coord,
        ax: Axes,
        params: dict[str, Any],
    ):
        extend = params["extend"]
        fill_range = params["fill_range"]
        direction = params["direction"]

        # Range
        if direction == "vertical":
            axis, other_axis = "x", "y"
        else:
            axis, other_axis = "y", "x"

        if isinstance(coord, coord_flip):
            axis, other_axis = other_axis, axis

        _axis = getattr(panel_params, axis)
        breaks = _axis.breaks
        range = _axis.range
        other_range = getattr(panel_params, other_axis).range

        if fill_range == "auto":
            if isinstance(_axis.scale, scale_discrete):
                fill_range = "nocycle"
            else:
                fill_range = "cycle"

        # Breaks along the width
        n_stripes = len(breaks)
        if n_stripes > 1:
            diff = np.diff(breaks)
            step = diff[0]
            equal_spaces = np.all(diff == step)
            if not equal_spaces:
                raise ValueError(
                    "The major breaks are not equally spaced. "
                    "We cannot create stripes."
                )
        else:
            step = breaks[0]

        deltas = np.array([step / 2] * n_stripes)
        many_stripes = len(breaks) > 1
        xmin = breaks - deltas
        xmax = breaks + deltas
        if fill_range in ("cycle", "nocycle") and many_stripes:
            if range[0] < breaks[0]:
                n_stripes += 1
                xmax = np.insert(xmax, 0, xmin[0])
                xmin = np.insert(xmin, 0, range[0])
            if range[1] > breaks[1]:
                n_stripes += 1
                xmin = np.append(xmin, xmax[-1])
                xmax = np.append(xmax, range[1])

        # Height
        full_height = other_range[1] - other_range[0]
        ymin = other_range[0] + full_height * extend[0]
        ymax = other_range[0] + full_height * extend[1]
        fill = list(islice(cycle(params["fill"]), n_stripes))
        if fill_range == "nocycle" and many_stripes:
            # there are at least two stripes at this point
            fill[0] = fill[1]
            fill[-1] = fill[-2]

        if direction != "vertical":
            xmin, xmax, ymin, ymax = ymin, ymax, xmin, xmax

        data = pd.DataFrame(
            {
                "xmin": xmin,
                "xmax": xmax,
                "ymin": ymin,
                "ymax": ymax,
                "fill": fill,
                "alpha": params["alpha"],
                "color": params["color"],
                "linetype": params["linetype"],
                "size": params["size"],
            }
        )

        return geom_rect.draw_group(data, panel_params, coord, ax, params)

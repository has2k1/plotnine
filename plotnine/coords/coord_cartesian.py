from __future__ import annotations

import typing
from types import SimpleNamespace

from ..iapi import panel_view
from ..positions.position import transform_position
from .coord import coord, dist_euclidean

if typing.TYPE_CHECKING:
    from typing import Any

    import pandas as pd

    from plotnine.iapi import scale_view
    from plotnine.scales.scale import scale
    from plotnine.typing import (
        FloatArray,
        FloatSeries,
    )


class coord_cartesian(coord):
    """
    Cartesian coordinate system

    Parameters
    ----------
    xlim :
        Limits (in data type of the x-aesthetic) for x axis.
        If None, then they are automatically computed.
    ylim :
        Limits (in data type of the x-aesthetic) for y axis.
        If None, then they are automatically computed.
    expand :
        If `True`, expand the coordinate axes by some factor. If `False`,
        use the limits from the data.
    """

    is_linear = True

    def __init__(
        self,
        xlim: tuple[Any, Any] | None = None,
        ylim: tuple[Any, Any] | None = None,
        expand: bool = True,
    ):
        self.limits = SimpleNamespace(x=xlim, y=ylim)
        self.expand = expand

    def transform(
        self, data: pd.DataFrame, panel_params: panel_view, munch: bool = False
    ) -> pd.DataFrame:
        from mizani.bounds import squish_infinite

        def squish_infinite_x(col: FloatSeries) -> FloatArray:
            return squish_infinite(col, range=panel_params.x.range)

        def squish_infinite_y(col: FloatSeries) -> FloatArray:
            return squish_infinite(col, range=panel_params.y.range)

        return transform_position(data, squish_infinite_x, squish_infinite_y)

    def setup_panel_params(self, scale_x: scale, scale_y: scale) -> panel_view:
        """
        Compute the range and break information for the panel
        """
        from mizani.transforms import identity_trans

        from plotnine.scales.scale_continuous import scale_continuous

        def get_scale_view(
            scale: scale, limits: tuple[Any, Any]
        ) -> scale_view:
            coord_limits = (
                scale.transform(limits)
                if limits and isinstance(scale, scale_continuous)
                else limits
            )
            expansion = scale.default_expansion(expand=self.expand)
            ranges = scale.expand_limits(
                scale.final_limits, expansion, coord_limits, identity_trans()
            )
            sv = scale.view(limits=coord_limits, range=ranges.range)
            return sv

        out = panel_view(
            x=get_scale_view(scale_x, self.limits.x),
            y=get_scale_view(scale_y, self.limits.y),
        )
        return out

    def distance(
        self,
        x: FloatSeries,
        y: FloatSeries,
        panel_params: panel_view,
    ) -> FloatArray:
        max_dist = dist_euclidean(panel_params.x.range, panel_params.y.range)[
            0
        ]
        return dist_euclidean(x, y) / max_dist

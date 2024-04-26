from __future__ import annotations

import typing
from types import SimpleNamespace as NS
from warnings import warn

from ..exceptions import PlotnineWarning
from ..iapi import panel_ranges, panel_view
from ..positions.position import transform_position
from .coord import coord, dist_euclidean

if typing.TYPE_CHECKING:
    from typing import Optional

    import pandas as pd
    from mizani.transforms import trans

    from plotnine.iapi import scale_view
    from plotnine.scales.scale import scale
    from plotnine.typing import (
        FloatArray,
        FloatSeries,
        TFloatArrayLike,
        TupleFloat2,
    )


class coord_trans(coord):
    """
    Transformed cartesian coordinate system

    Parameters
    ----------
    x : str | trans
        Name of transform or `trans` class to transform the x axis
    y : str | trans
        Name of transform or `trans` class to transform the y axis
    xlim : tuple[float, float]
        Limits for x axis. If None, then they are automatically computed.
    ylim : tuple[float, float]
        Limits for y axis. If None, then they are automatically computed.
    expand : bool
        If `True`, expand the coordinate axes by some factor. If `False`,
        use the limits from the data.
    """

    trans_x: trans
    trans_y: trans

    def __init__(
        self,
        x: str | trans = "identity",
        y: str | trans = "identity",
        xlim: Optional[TupleFloat2] = None,
        ylim: Optional[TupleFloat2] = None,
        expand: bool = True,
    ):
        from mizani.transforms import gettrans

        self.trans_x = gettrans(x)
        self.trans_y = gettrans(y)
        self.limits = NS(x=xlim, y=ylim)
        self.expand = expand

    def transform(
        self, data: pd.DataFrame, panel_params: panel_view, munch: bool = False
    ) -> pd.DataFrame:
        from mizani.bounds import squish_infinite

        if not self.is_linear and munch:
            data = self.munch(data, panel_params)

        def trans_x(col: FloatSeries) -> FloatSeries:
            result = transform_value(self.trans_x, col, panel_params.x.range)
            if any(result.isna()):
                warn(
                    "Coordinate transform of x aesthetic "
                    "created one or more NaN values.",
                    PlotnineWarning,
                )
            return result

        def trans_y(col: FloatSeries) -> FloatSeries:
            result = transform_value(self.trans_y, col, panel_params.y.range)
            if any(result.isna()):
                warn(
                    "Coordinate transform of y aesthetic "
                    "created one or more NaN values.",
                    PlotnineWarning,
                )
            return result

        data = transform_position(data, trans_x, trans_y)
        return transform_position(data, squish_infinite, squish_infinite)

    def backtransform_range(self, panel_params: panel_view) -> panel_ranges:
        return panel_ranges(
            x=self.trans_x.inverse(panel_params.x.range),
            y=self.trans_y.inverse(panel_params.y.range),
        )

    def setup_panel_params(self, scale_x: scale, scale_y: scale) -> panel_view:
        """
        Compute the range and break information for the panel
        """

        def get_scale_view(
            scale: scale, coord_limits: TupleFloat2, trans: trans
        ) -> scale_view:
            if coord_limits:
                coord_limits = trans.transform(coord_limits)

            expansion = scale.default_expansion(expand=self.expand)
            ranges = scale.expand_limits(
                scale.limits, expansion, coord_limits, trans
            )
            sv = scale.view(limits=coord_limits, range=ranges.range)
            sv.range = tuple(sorted(ranges.range_coord))  # type: ignore
            sv.breaks = transform_value(
                trans,
                # TODO: fix typecheck
                sv.breaks,  # type: ignore
                sv.range,
            )
            sv.minor_breaks = transform_value(
                trans,
                sv.minor_breaks,
                sv.range,
            )
            return sv

        out = panel_view(
            x=get_scale_view(scale_x, self.limits.x, self.trans_x),
            y=get_scale_view(scale_y, self.limits.y, self.trans_y),
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
        xt = self.trans_x.transform(x)
        yt = self.trans_y.transform(y)
        return dist_euclidean(xt, yt) / max_dist


def transform_value(
    trans: trans, value: TFloatArrayLike, range: TupleFloat2
) -> TFloatArrayLike:
    """
    Transform value
    """
    return trans.transform(value)

from __future__ import annotations

import typing
from types import SimpleNamespace

from ..iapi import panel_view
from ..positions.position import transform_position
from .coord import coord, dist_euclidean

if typing.TYPE_CHECKING:
    from typing import Optional

    import pandas as pd

    from plotnine.iapi import scale_view
    from plotnine.scales.scale import scale
    from plotnine.typing import (
        FloatArray,
        FloatSeries,
        TupleFloat2,
    )


class coord_cartesian(coord):
    """
    Cartesian coordinate system

    Parameters
    ----------
    xlim : tuple[float, float], default=None
        Limits for x axis. If None, then they are automatically computed.
    ylim : tuple[float, float], default=None
        Limits for y axis. If None, then they are automatically computed.
    expand : bool, default=True
        If `True`, expand the coordinate axes by some factor. If `False`,
        use the limits from the data.
    """

    is_linear = True

    def __init__(
        self,
        xlim: Optional[TupleFloat2] = None,
        ylim: Optional[TupleFloat2] = None,
        expand: bool = True,
    ):
        self.limits = SimpleNamespace(x=xlim, y=ylim)
        self.expand = expand

    def transform(
        self, data: pd.DataFrame, panel_params: panel_view, munch: bool = False
    ) -> pd.DataFrame:
        from mizani.bounds import squish_infinite

        def squish_infinite_x(col):
            return squish_infinite(col, range=panel_params.x.range)

        def squish_infinite_y(col):
            return squish_infinite(col, range=panel_params.y.range)

        return transform_position(data, squish_infinite_x, squish_infinite_y)

    def setup_panel_params(self, scale_x: scale, scale_y: scale) -> panel_view:
        """
        Compute the range and break information for the panel
        """
        from mizani.transforms import identity_trans

        def get_scale_view(
            scale: scale, coord_limits: TupleFloat2
        ) -> scale_view:
            expansion = scale.default_expansion(expand=self.expand)
            ranges = scale.expand_limits(
                scale.limits, expansion, coord_limits, identity_trans
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

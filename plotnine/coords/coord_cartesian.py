from __future__ import annotations

import typing
from types import SimpleNamespace

from mizani.bounds import squish_infinite
from mizani.transforms import identity_trans

from ..iapi import panel_view
from ..positions.position import transform_position
from .coord import coord, dist_euclidean

if typing.TYPE_CHECKING:
    from typing import Optional

    import numpy as np
    import numpy.typing as npt
    import pandas as pd

    import plotnine as p9


class coord_cartesian(coord):
    """
    Cartesian coordinate system

    Parameters
    ----------
    xlim : None | (float, float)
        Limits for x axis. If None, then they are
        automatically computed.
    ylim : None | (float, float)
        Limits for y axis. If None, then they are
        automatically computed.
    expand : bool
        If `True`, expand the coordinate axes by
        some factor. If `False`, use the limits
        from the data.
    """

    is_linear = True

    def __init__(
        self,
        xlim: Optional[tuple[float, float]] = None,
        ylim: Optional[tuple[float, float]] = None,
        expand: bool = True
    ) -> None:
        self.limits = SimpleNamespace(x=xlim, y=ylim)
        self.expand = expand

    def transform(
        self,
        data: pd.DataFrame,
        panel_params: p9.iapi.panel_view,
        munch: bool = False
    ) -> pd.DataFrame:
        def squish_infinite_x(data: pd.DataFrame) -> pd.DataFrame:
            return squish_infinite(  # type: ignore
                data,
                range=panel_params.x.range
            )

        def squish_infinite_y(data: pd.DataFrame) -> pd.DataFrame:
            return squish_infinite(  # type: ignore
                data,
                range=panel_params.y.range
            )

        return transform_position(data, squish_infinite_x, squish_infinite_y)

    def setup_panel_params(
        self,
        scale_x: p9.scales.scale.scale,
        scale_y: p9.scales.scale.scale
    ) -> p9.iapi.panel_view:
        """
        Compute the range and break information for the panel
        """
        def get_scale_view(
            scale: p9.scales.scale.scale,
            coord_limits: tuple[float, float]
        ) -> p9.iapi.scale_view:
            expansion = scale.default_expansion(expand=self.expand)
            ranges = scale.expand_limits(
                scale.limits, expansion, coord_limits, identity_trans
            )
            sv = scale.view(limits=coord_limits, range=ranges.range)
            return sv

        out = panel_view(
            x=get_scale_view(scale_x, self.limits.x),
            y=get_scale_view(scale_y, self.limits.y)
        )
        return out

    def distance(
        self,
        x: pd.Series[float],
        y: pd.Series[float],
        panel_params: p9.iapi.panel_view
    ) -> npt.NDArray[np.float64]:
        max_dist = dist_euclidean(
            panel_params.x.range,
            panel_params.y.range
        )[0]
        return dist_euclidean(x, y) / max_dist  # type: ignore

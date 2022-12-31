from __future__ import annotations

import typing
from types import SimpleNamespace as NS
from typing import overload
from warnings import warn

import numpy as np
from mizani.bounds import squish_infinite
from mizani.transforms import gettrans

from ..exceptions import PlotnineWarning
from ..iapi import panel_ranges, panel_view
from ..positions.position import transform_position
from .coord import coord, dist_euclidean

if typing.TYPE_CHECKING:
    from typing import Optional, Sequence

    import mizani as mz
    import numpy.typing as npt
    import pandas as pd

    import plotnine as p9


class coord_trans(coord):
    """
    Transformed cartesian coordinate system

    Parameters
    ----------
    x : str | trans
        Name of transform or `trans` class to
        transform the x axis
    y : str | trans
        Name of transform or `trans` class to
        transform the y axis
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

    trans_x: mz.transforms.trans
    trans_y: mz.transforms.trans

    def __init__(
        self,
        x: str | mz.transforms.trans = 'identity',
        y: str | mz.transforms.trans = 'identity',
        xlim: Optional[tuple[float, float]] = None,
        ylim: Optional[tuple[float, float]] = None,
        expand: bool = True
    ) -> None:
        self.trans_x = gettrans(x)
        self.trans_y = gettrans(y)
        self.limits = NS(x=xlim, y=ylim)
        self.expand = expand

    def transform(
        self,
        data: pd.DataFrame,
        panel_params: panel_view,
        munch: bool = False
    ) -> pd.DataFrame:
        if not self.is_linear and munch:
            data = self.munch(data, panel_params)

        def trans_x(data: pd.DataFrame) -> pd.DataFrame:
            result = transform_value(  # type: ignore
                self.trans_x,
                data,
                panel_params.x.range
            )
            if any(result.isnull()):
                warn(
                    "Coordinate transform of x aesthetic "
                    "created one or more NaN values.",
                    PlotnineWarning
                )
            return result  # type: ignore

        def trans_y(data: pd.DataFrame) -> pd.DataFrame:
            result = transform_value(  # type: ignore
                self.trans_y,
                data,
                panel_params.y.range
            )
            if any(result.isnull()):
                warn(
                    "Coordinate transform of y aesthetic "
                    "created one or more NaN values.",
                    PlotnineWarning
                )
            return result  # type: ignore

        data = transform_position(data, trans_x, trans_y)
        return transform_position(data, squish_infinite, squish_infinite)

    def backtransform_range(
        self,
        panel_params: p9.iapi.panel_view
    ) -> panel_ranges:
        return panel_ranges(
            x=self.trans_x.inverse(panel_params.x.range),
            y=self.trans_y.inverse(panel_params.y.range)
        )

    def setup_panel_params(
        self,
        scale_x: p9.scales.scale.scale,
        scale_y: p9.scales.scale.scale
    ) -> panel_view:
        """
        Compute the range and break information for the panel
        """
        def get_scale_view(
            scale: p9.scales.scale.scale,
            coord_limits: tuple[float, float],
            trans: mz.transforms.trans
        ) -> p9.iapi.scale_view:
            if coord_limits:
                coord_limits = trans.transform(coord_limits)

            expansion = scale.default_expansion(expand=self.expand)
            ranges = scale.expand_limits(
                scale.limits, expansion, coord_limits, trans
            )
            sv = scale.view(limits=coord_limits, range=ranges.range)
            sv.range = tuple(sorted(ranges.range_coord))  # type: ignore
            assert not isinstance(sv.breaks, dict)
            sv.breaks = transform_value(trans, sv.breaks, sv.range)
            sv.minor_breaks = transform_value(trans, sv.minor_breaks, sv.range)
            return sv

        out = panel_view(
            x=get_scale_view(scale_x, self.limits.x, self.trans_x),
            y=get_scale_view(scale_y, self.limits.y, self.trans_y)
        )
        return out

    def distance(
        self,
        x: pd.Series[float],
        y: pd.Series[float],
        panel_params: panel_view
    ) -> npt.NDArray[np.float64]:
        max_dist = dist_euclidean(
            panel_params.x.range,
            panel_params.y.range
        )[0]
        xt = self.trans_x.transform(x)
        yt = self.trans_y.transform(y)
        return dist_euclidean(xt, yt) / max_dist  # type: ignore


@overload
def transform_value(
    trans: mz.transforms.trans,
    value: pd.Series[float],
    range: tuple[float, float]
) -> pd.Series[float]:
    ...


@overload
def transform_value(
    trans: mz.transforms.trans,
    value: Sequence[float],
    range: tuple[float, float]
) -> Sequence[float]:
    ...


def transform_value(
    trans: mz.transforms.trans,
    value: pd.Series[float] | Sequence[float],
    range: tuple[float, float]
) -> pd.Series[float] | Sequence[float]:
    """
    Transform value
    """
    return trans.transform(value)  # type: ignore

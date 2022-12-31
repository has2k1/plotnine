from __future__ import annotations

import typing
from typing import overload

from ..iapi import panel_ranges, panel_view
from .coord_cartesian import coord_cartesian

if typing.TYPE_CHECKING:
    import pandas as pd

    import plotnine as p9

    from ..iapi import labels_view


class coord_flip(coord_cartesian):
    """
    Flipped cartesian coordinates

    The horizontal becomes vertical, and vertical becomes
    horizontal. This is primarily useful for converting
    geoms and statistics which display y conditional
    on x, to x conditional on y.

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

    def labels(
        self,
        cur_labels: p9.iapi.labels_view
    ) -> p9.iapi.labels_view:
        return flip_labels(super().labels(cur_labels))

    def transform(
        self,
        data: pd.DataFrame,
        panel_params: p9.iapi.panel_view,
        munch: bool = False
    ) -> pd.DataFrame:
        data = flip_labels(data)
        return super().transform(data, panel_params, munch=munch)

    def setup_panel_params(
        self,
        scale_x: p9.scales.scale.scale,
        scale_y: p9.scales.scale.scale
    ) -> p9.iapi.panel_view:
        panel_params = super().setup_panel_params(scale_x, scale_y)
        return flip_labels(panel_params)

    def setup_layout(self, layout: pd.DataFrame) -> pd.DataFrame:
        # switch the scales
        x, y = 'SCALE_X', 'SCALE_Y'
        layout[x], layout[y] = layout[y].copy(), layout[x].copy()
        return layout

    def range(
        self,
        panel_params: p9.iapi.panel_view
    ) -> panel_ranges:
        """
        Return the range along the dimensions of the coordinate system
        """
        # Defaults to providing the 2D x-y ranges
        return panel_ranges(
            x=panel_params.y.range,
            y=panel_params.x.range
        )


@overload
def flip_labels(obj: pd.DataFrame) -> pd.DataFrame: ...


@overload
def flip_labels(obj: labels_view) -> labels_view: ...


@overload
def flip_labels(obj: panel_view) -> panel_view: ...


def flip_labels(
    obj: pd.DataFrame | labels_view | panel_view
) -> pd.DataFrame | labels_view | panel_view:
    """
    Rename fields x to y and y to x

    Parameters
    ----------
    obj : dict_like | types.SimpleNamespace
        Object with labels to rename
    """
    def sub(a: str, b: str) -> None:
        """
        Substitute all keys that start with a to b
        """
        for label in list(obj.keys()):  # type: ignore
            if label.startswith(a):
                new_label = b+label[1:]
                obj[new_label] = obj.pop(label)  # type: ignore

    if hasattr(obj, 'keys'):  # dict or dataframe
        sub('x', 'z')
        sub('y', 'x')
        sub('z', 'y')
    elif hasattr(obj, 'x') and hasattr(obj, 'y'):
        obj.x, obj.y = obj.y, obj.x

    return obj

from __future__ import annotations

import typing

import pandas as pd

from ..iapi import labels_view, panel_ranges, panel_view
from .coord_cartesian import coord_cartesian

if typing.TYPE_CHECKING:
    from typing import Sequence, TypeVar

    from plotnine.scales.scale import scale

    THasLabels = TypeVar(
        "THasLabels", bound=pd.DataFrame | labels_view | panel_view
    )


class coord_flip(coord_cartesian):
    """
    Flipped cartesian coordinates

    The horizontal becomes vertical, and vertical becomes horizontal.
    This is primarily useful for converting geoms and statistics which
    display y conditional on x, to x conditional on y.

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

    def labels(self, cur_labels: labels_view) -> labels_view:
        return flip_labels(super().labels(cur_labels))

    def transform(
        self, data: pd.DataFrame, panel_params: panel_view, munch: bool = False
    ) -> pd.DataFrame:
        data = flip_labels(data)
        return super().transform(data, panel_params, munch=munch)

    def setup_panel_params(self, scale_x: scale, scale_y: scale) -> panel_view:
        panel_params = super().setup_panel_params(scale_x, scale_y)
        return flip_labels(panel_params)

    def setup_layout(self, layout: pd.DataFrame) -> pd.DataFrame:
        # switch the scales
        x, y = "SCALE_X", "SCALE_Y"
        layout[x], layout[y] = layout[y].copy(), layout[x].copy()
        return layout

    def range(self, panel_params: panel_view) -> panel_ranges:
        """
        Return the range along the dimensions of the coordinate system
        """
        # Defaults to providing the 2D x-y ranges
        return panel_ranges(x=panel_params.y.range, y=panel_params.x.range)


def flip_labels(obj: THasLabels) -> THasLabels:
    """
    Rename fields x to y and y to x

    Parameters
    ----------
    obj : dict_like | dataclass
        Object with labels to rename
    """

    def sub(a: str, b: str, df: pd.DataFrame):
        """
        Substitute all keys that start with a to b
        """
        columns: Sequence[str] = df.columns.tolist()
        for label in columns:
            if label.startswith(a):
                new_label = b + label[1:]
                df[new_label] = df.pop(label)

    if isinstance(obj, pd.DataFrame):
        sub("x", "z", obj)
        sub("y", "x", obj)
        sub("z", "y", obj)
    elif isinstance(obj, (labels_view, panel_view)):
        obj.x, obj.y = obj.y, obj.x  # type: ignore

    return obj

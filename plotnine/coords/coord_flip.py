from __future__ import annotations

from typing import TYPE_CHECKING, cast

import narwhals as nw

from .._utils import frame
from ..iapi import labels_view, panel_ranges, panel_view
from .coord_cartesian import coord_cartesian

if TYPE_CHECKING:
    from typing import TypeVar

    from plotnine._utils.frame import DataFrame
    from plotnine.scales.scale import scale
    from plotnine.typing import Side

    THasLabels = TypeVar(
        "THasLabels", bound="DataFrame | labels_view | panel_view"
    )


_FLIP_POSITION: dict[Side, Side] = {
    "top": "right",
    "bottom": "left",
    "left": "bottom",
    "right": "top",
}


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

    @property
    def preserves_dimensions(self) -> bool:
        return False

    def labels(self, cur_labels: labels_view) -> labels_view:
        return flip_labels(super().labels(cur_labels))

    def transform(
        self, data: DataFrame, panel_params: panel_view, munch: bool = False
    ) -> DataFrame:
        data = flip_labels(data)
        return super().transform(data, panel_params, munch=munch)

    def setup_panel_params(self, scale_x: scale, scale_y: scale) -> panel_view:
        panel_params = super().setup_panel_params(scale_x, scale_y)
        panel_params = flip_labels(panel_params)
        # The axis position rotates with the flip (matches ggplot2's
        # scale_flip_axis): top->right, bottom->left, left->bottom, right->top
        panel_params.x.position = _FLIP_POSITION[panel_params.x.position]
        panel_params.y.position = _FLIP_POSITION[panel_params.y.position]
        for sv in (panel_params.x, panel_params.y):
            if sv.sec is not None:
                sv.sec.position = _FLIP_POSITION[cast("Side", sv.sec.position)]
        return panel_params

    def setup_layout(self, layout: DataFrame) -> DataFrame:
        # switch the scales
        return layout.with_columns(
            SCALE_X=nw.col("SCALE_Y"), SCALE_Y=nw.col("SCALE_X")
        )

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
    obj : dataframe | dataclass
        Object with labels to rename
    """

    def flip(label: str) -> str:
        if label.startswith("x"):
            return "y" + label[1:]
        elif label.startswith("y"):
            return "x" + label[1:]
        return label

    if isinstance(obj, (labels_view, panel_view)):
        obj.x, obj.y = obj.y, obj.x  # type: ignore
    elif isinstance(obj, nw.DataFrame) or frame.is_frame(obj):
        df = frame.to_frame(obj)
        df = df.rename({c: flip(c) for c in df.columns if flip(c) != c})
        return cast(
            "THasLabels",
            df if isinstance(obj, nw.DataFrame) else df.to_native(),
        )

    return obj

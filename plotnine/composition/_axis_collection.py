"""
Resolve axis titles without building plots
"""

from __future__ import annotations

from copy import copy
from typing import TYPE_CHECKING, cast

from .._utils import OPPOSITE_SIDE

if TYPE_CHECKING:
    from typing import Iterable

    from plotnine import ggplot, theme
    from plotnine.scales.scale_xy import ScaleX, ScaleY
    from plotnine.typing import Side


AXIS_TEXT_AND_TICKS: dict[Side, tuple[str, str, str]] = {
    "bottom": (
        "axis_text_x_bottom",
        "axis_ticks_major_x_bottom",
        "axis_ticks_minor_x_bottom",
    ),
    "top": (
        "axis_text_x_top",
        "axis_ticks_major_x_top",
        "axis_ticks_minor_x_top",
    ),
    "left": (
        "axis_text_y_left",
        "axis_ticks_major_y_left",
        "axis_ticks_minor_y_left",
    ),
    "right": (
        "axis_text_y_right",
        "axis_ticks_major_y_right",
        "axis_ticks_minor_y_right",
    ),
}
"""
Themeable names for axis ticks and tick labels, indexed by side
"""

AXIS_TITLE: dict[Side, str] = {
    "bottom": "axis_title_x_bottom",
    "top": "axis_title_x_top",
    "left": "axis_title_y_left",
    "right": "axis_title_y_right",
}
"""
Themeable name for each axis title, indexed by side
"""


def axis_titles(plot: ggplot) -> dict[Side, str]:
    """
    Resolve a plot's axis titles by side without building it

    A position scale's name overrides its mapped label. A secondary axis
    titles the side opposite its primary, and the coordinate system can
    swap the x and y labels. Omit sides without titles.

    Resolve labels on a copy to preserve the plot's unbuilt state.

    Parameters
    ----------
    plot :
        Plot to inspect, whether built or unbuilt.

    Returns
    -------
    :
        Title text for each side that has one.
    """
    labels = copy(plot.labels)
    labels.add_defaults(plot.mapping.labels)
    plot.layers.update_labels(labels)
    labels = plot.coordinates.labels(labels)
    # The scale annotation permits strings, but every position is a `Side`.
    x_side, y_side = cast("tuple[Side, Side]", plot.scales.axis_positions)

    titles: dict[Side, str] = {}
    positions: tuple[tuple[Side, ScaleX | ScaleY | None, str | None], ...] = (
        (x_side, plot.scales.x, labels.x),
        (y_side, plot.scales.y, labels.y),
    )
    for side, scale, label in positions:
        name = scale.name if scale is not None else None
        title = name or label or ""
        if title:
            titles[side] = title

        # Discrete position scales do not support secondary axes.
        sec = getattr(scale, "sec_axis", None)
        if sec is not None:
            sec_title = title if sec.name is None else sec.name
            if sec_title:
                titles[OPPOSITE_SIDE[side]] = sec_title

    return titles


def blank_theme(names: Iterable[str]) -> theme:
    """
    Return a theme that blanks the named themeables

    Parameters
    ----------
    names :
        Themeable names.

    Returns
    -------
    :
        Theme that sets each name to `element_blank`.
    """
    from plotnine import element_blank, theme

    return theme(**{name: element_blank() for name in names})  # pyright: ignore[reportArgumentType]

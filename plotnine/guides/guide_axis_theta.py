from __future__ import annotations

from dataclasses import dataclass, field

from ..themes.theme import theme as Theme


@dataclass
class guide_axis_theta:
    """
    Theta-axis guide for radial coordinates.

    This guide is consumed by ``coord_radial`` when it draws theta-axis
    tick labels. It is not drawn as a legend or colorbar.
    """

    title: str | None = None
    """Title of the guide. Currently unused."""

    theme: Theme = field(default_factory=Theme)
    """A theme to style the guide. Currently unused."""

    angle: float | None = None
    """
    Angle in degrees at which to draw theta-axis tick labels.

    If ``None``, Matplotlib's default theta tick label rotation is used.
    """

    minor_ticks: bool | None = None
    """Whether to draw minor ticks. Currently unused."""

    cap: bool | None = None
    """Whether to cap the axis line. Currently unused."""

    order: int = 0
    """Order of this guide among multiple guides. Currently unused."""

    position: str | None = None
    """Guide position. Currently unused."""

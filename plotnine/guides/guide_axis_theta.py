from __future__ import annotations

from dataclasses import dataclass, field

from ..themes.theme import theme as Theme


@dataclass
class guide_axis_theta:
    """
    Theta-axis guide for radial coordinates.

    A specialized guide used in :class:`~plotnine.coords.coord_radial` to
    control how tick labels are rendered on the theta (angular) axis.
    Unlike legend-style guides, this guide is not drawn as a box or colorbar;
    it is consumed directly by ``coord_radial`` when it positions and rotates
    the outer tick labels.

    Parameters
    ----------
    title :
        Title for the guide.  Currently unused; theta-axis labels do not
        display a title in Matplotlib's polar axes.
    theme :
        A :class:`~plotnine.themes.theme.theme` object to style the guide
        individually.  Currently unused.
    angle :
        Orientation of the tick labels, in degrees, measured as an offset
        from the **tangential direction** at each tick position.

        * ``None`` (default) - labels are not rotated by this guide; the
          Matplotlib default (horizontal, i.e. ``0`` absolute) is used.
        * ``0`` - labels are oriented tangentially, parallel to the arc.
          This matches the ggplot2 heuristic default and is the most common
          choice.
        * ``90`` - labels point radially outward along the spoke.
        * Any other float - a corresponding offset from the tangential
          direction.

        .. note::
           This differs from Matplotlib's ``tick_params(labelrotation=N)``,
           which treats ``N`` as an **absolute** angle.  Here ``angle`` is
           always relative to the tangent at each label's position.

    minor_ticks :
        Whether to draw minor ticks.  Not yet implemented; the value is
        stored but has no effect.
    cap :
        Whether to cap the axis line back to the outermost breaks.  Not
        yet implemented; the value is stored but has no effect.
    order :
        Order of this guide among multiple guides.  Not yet implemented.
    position :
        Guide position (``"top"``, ``"bottom"``, ``"left"``, or
        ``"right"``).  Not yet implemented.

    See Also
    --------
    :class:`~plotnine.coords.coord_radial` : The coordinate system that
        consumes this guide.
    plotnine.guides : Add guides to a plot with ``guides(theta=...)``.

    Examples
    --------
    Make theta labels follow the arc (tangential, matching ggplot2's default
    heuristic):

    .. code-block:: python

        from plotnine import ggplot, aes, geom_point, coord_radial, guides
        from plotnine.guides import guide_axis_theta
        from plotnine.data import mtcars

        (
            ggplot(mtcars, aes("disp", "mpg"))
            + geom_point()
            + coord_radial(theta_labels=True)
            + guides(theta=guide_axis_theta(angle=0))
        )

    .. note::
       ``coord_radial`` hides theta labels on full-circle plots by default
       (``theta_labels=False``).  You must pass ``theta_labels=True`` to
       ``coord_radial`` for this guide to have any visible effect.
    """

    title: str | None = None
    """Title of the guide. Currently unused."""

    theme: Theme = field(default_factory=Theme)
    """A theme to style the guide. Currently unused."""

    angle: float | None = None
    """
    Offset from the tangential direction in degrees.

    ``None`` keeps Matplotlib's default (horizontal labels).
    ``0`` makes labels tangential (parallel to the arc).
    ``90`` makes labels radial (pointing outward).
    """

    minor_ticks: bool | None = None
    """Whether to draw minor ticks. Not yet implemented."""

    cap: bool | None = None
    """Whether to cap the axis line. Not yet implemented."""

    order: int = 0
    """Order of this guide among multiple guides. Not yet implemented."""

    position: str | None = None
    """Guide position. Not yet implemented."""

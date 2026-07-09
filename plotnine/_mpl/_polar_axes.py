from __future__ import annotations

from typing import TYPE_CHECKING, cast

from matplotlib.projections import register_projection
from matplotlib.projections.polar import PolarAxes

if TYPE_CHECKING:
    from matplotlib.backend_bases import RendererBase
    from matplotlib.projections.polar import RadialAxis, ThetaAxis

    from plotnine.typing import PolarSide


class p9PolarAxes(PolarAxes):
    """
    PolarAxes that keeps the axis tick labels above the geom layers
    """

    name = "p9polar"

    _axis_at_side: dict[PolarSide, ThetaAxis | RadialAxis] | None = None

    # Whether the r-axis ticks already keep their themed styling across
    # matplotlib's tick resets. Guards `lock_raxis_tick_style` so repeated
    # calls do not stack wrappers on top of each other.
    _raxis_tick_style_locked: bool = False

    @property
    def axis_at_side(self) -> dict[PolarSide, ThetaAxis | RadialAxis]:
        """
        The theta/r axis artist occupying each active polar side
        """
        if self._axis_at_side is None:
            self._axis_at_side = {}
        return self._axis_at_side

    def draw(self, renderer: RendererBase) -> None:
        """
        Draw the axes, then lift the tick labels above the geoms

        With the default `panel_ontop=False` (`axisbelow=True`) the normal
        pass paints the gridlines and the tick labels below the geoms.
        Re-drawing the radial-axis and theta-axis tick labels keeps them
        visible on top of opaque geoms.
        When `panel_ontop=True` everything is already above the geoms, so
        the re-draw is a visual no-op.
        """
        super().draw(renderer)

        for axis in (self.raxis, self.thetaaxis):
            for label in axis.get_ticklabels():
                if label.get_visible():
                    label.draw(renderer)

    @property
    def thetaaxis(self) -> ThetaAxis:
        return cast("ThetaAxis", self.xaxis)

    @property
    def raxis(self) -> RadialAxis:
        return cast("RadialAxis", self.yaxis)

    def set_spine_visible(self, name: str, visible: bool) -> None:
        """
        Set a spine's visibility and block matplotlib's from overwriting it

        `PolarAxes.draw` derives `inner`/`start`/`end` spine visibility
        from pure geometry (donut hole present, arc partial) and paints
        the spine in that same call, so a plain `set_visible` on a spine
        is overwritten and never matters.
        """
        # This method makes the spine visible and replaces the spine's
        # own `set_visible` with a no-op function to block matplotlib's
        # internal call before it paints.
        spine = self.spines[name]
        spine_cls = type(spine)
        spine_cls.set_visible(spine, visible)

        def noop(b):
            pass

        spine.set_visible = noop

    def lock_raxis_tick_style(self) -> None:
        """
        Keep the r-axis ticks looking as the theme styled them across draws

        The theme styles the r-axis ticks and tick labels once, before any
        real render pass. On the first render `PolarAxes.draw` calls
        `self.yaxis.reset_ticks()`, which drops the lazily-cached tick lists;
        the next access rebuilds fresh `Tick` objects with matplotlib's
        default styling, so the themed colours, sizes and tick lengths are
        gone by the time those ticks are painted. This makes the r-axis ticks
        immune to that wipe. Only the r-axis needs it; `PolarAxes.draw` has no
        matching reset for the theta-axis.
        """
        # The reset and the paint that consumes it both happen inside a single
        # `PolarAxes.draw` call, so restoring styling after `draw` returns is
        # too late -- the default-styled ticks are already painted. Wrapping
        # `reset_ticks` instead closes the gap synchronously: the wrapper
        # re-copies the styling from the pre-reset ticks onto the fresh ones
        # before control returns to `PolarAxes.draw`, so every tick the axis
        # then grows and paints inherits the themed look. Capturing the source
        # styling live on each reset (rather than from a one-off snapshot)
        # keeps this re-entrant across any number of redraws.
        if self._raxis_tick_style_locked:
            return
        self._raxis_tick_style_locked = True

        axis = self.raxis
        reset_ticks = axis.reset_ticks

        def reset_ticks_and_restyle() -> None:
            # `_copy_tick_props` is matplotlib's own routine for propagating
            # the look of `majorTicks[0]` onto the sibling ticks it grows, so
            # reusing it leaves the restored ticks identical to freshly grown
            # ones -- covering label1/label2, tick1line/tick2line and the tick
            # length, for both major and minor ticks.
            major, minor = axis.majorTicks[0], axis.minorTicks[0]
            reset_ticks()
            axis._copy_tick_props(major, axis.majorTicks[0])  # type: ignore
            axis._copy_tick_props(minor, axis.minorTicks[0])  # type: ignore

        axis.reset_ticks = reset_ticks_and_restyle


register_projection(p9PolarAxes)

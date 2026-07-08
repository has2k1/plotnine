from __future__ import annotations

from typing import TYPE_CHECKING, cast

from matplotlib.projections import register_projection
from matplotlib.projections.polar import PolarAxes

if TYPE_CHECKING:
    from matplotlib.backend_bases import RendererBase
    from matplotlib.projections.polar import RadialAxis, ThetaAxis


class p9PolarAxes(PolarAxes):
    """
    PolarAxes that keeps the axis tick labels above the geom layers
    """

    name = "p9polar"

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


register_projection(p9PolarAxes)

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

        `PolarAxes.draw` also derives `inner`/`start`/`end` spine
        visibility from pure geometry (donut hole present, arc partial),
        discarding whatever axis_line theming chose. Theming always sets
        every one of these three spines (blank or not) before the first
        real draw, so saving their visibility beforehand and restoring
        it right after `super().draw()` makes that choice stick.
        """
        spine_names = ("inner", "start", "end")
        visible = {
            name: self.spines[name].get_visible() for name in spine_names
        }

        super().draw(renderer)

        for name, is_visible in visible.items():
            self.spines[name].set_visible(is_visible)

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


register_projection(p9PolarAxes)

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from matplotlib import cbook
from matplotlib.projections import register_projection
from matplotlib.projections.polar import PolarAxes, RadialAxis, ThetaAxis

from ._radial_axis import (
    p9RadialAxis,
    p9SecondaryRadialAxis,
    p9ThetaAxis,
    p9ThetaTick,
)
from .axes import register_lim_changed_signal

if TYPE_CHECKING:
    from matplotlib.backend_bases import RendererBase

    from plotnine.typing import PolarSide


class p9RadialAxes(PolarAxes):
    """
    Polar axes that keeps the axis tick labels above the geom layers
    """

    name = "p9radial"

    _shared_axes = {
        **PolarAxes._shared_axes,  # pyright: ignore[reportAttributeAccessIssue]
        "sec_r": cbook.Grouper(),
    }

    _axis_at_side: dict[PolarSide, ThetaAxis | RadialAxis] | None = None

    # Secondary r-axis drawn at the end spoke; None until first requested.
    _sec_raxis: p9RadialAxis | None = None

    # Whether the r-axis ticks already keep their themed styling across
    # matplotlib's tick resets. Guards `lock_raxis_tick_style` so repeated
    # calls do not stack wrappers on top of each other.
    _raxis_tick_style_locked: bool = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_theta_zero_location("N")  # 12 o'clock
        self.set_spine_visible("start", False)
        self.set_spine_visible("end", False)

    def _init_axis(self) -> None:
        """
        Polar panel axes with plotnine's theta and radial tick geometry
        """
        self.xaxis = p9ThetaAxis(self, clear=False)
        self.yaxis = p9RadialAxis(self, clear=False)
        self.spines["polar"].register_axis(self.yaxis)
        if inner_spine := self.spines.get("inner"):
            inner_spine.register_axis(self.yaxis)

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
        Draw the axes, then lift the r-axis ticks above the geoms

        With the default `panel_ontop=False` (`axisbelow=True`) the normal
        pass paints the gridlines, tick marks and tick labels below the
        geoms. Re-drawing each r-axis's tick marks and labels keeps them
        visible on top of opaque geoms and above the theta gridlines that
        cross them on the shared full-circle spoke.
        When `panel_ontop=True` everything is already above the geoms, so
        the re-draw is a visual no-op.
        """
        for tick in (*self.raxis.majorTicks, *self.raxis.minorTicks):
            tick.update_position(tick.get_loc())

        if self._sec_raxis:
            for tick in (
                *self._sec_raxis.majorTicks,
                *self._sec_raxis.minorTicks,
            ):
                tick.update_position(tick.get_loc())

        super().draw(renderer)

        _redraw_raxis(self.raxis, renderer)
        if self._sec_raxis:
            _redraw_raxis(self._sec_raxis, renderer)

        for tick in (*self.thetaaxis.majorTicks, *self.thetaaxis.minorTicks):
            if not isinstance(tick, p9ThetaTick):
                continue
            tick._position_labels(renderer)
            for label in (tick.label1, tick.label2):
                if label.get_visible():
                    label.draw(renderer)

    @property
    def thetaaxis(self) -> ThetaAxis:
        return cast("ThetaAxis", self.xaxis)

    @property
    def raxis(self) -> p9RadialAxis:
        return cast("p9RadialAxis", self.yaxis)

    def add_sec_raxis(self) -> p9RadialAxis:
        """
        Return the secondary r-axis drawn at the end spoke, creating it once

        The axis starts with no ticks or labels; the caller sets them via
        `set_ticks` / `set_ticklabels`.  It is registered in
        `axis_at_side["r_end"]` and its tick labels are redrawn above geoms
        on every `draw` call, mirroring the primary r-axis behaviour.

        Returns
        -------
        :
            The secondary radial axis anchored to the end spoke.
        """
        if self._sec_raxis:
            return self._sec_raxis

        axis = p9SecondaryRadialAxis(self, clear=True)
        # Register so mpl can resolve _get_axis_name(), and add to the
        # draw tree.  Mirrors the pattern in p9Axes._make_sec_axis.
        self._axis_map["sec_r"] = axis
        register_lim_changed_signal(self, "sec_r")
        self.add_artist(axis)
        axis.set_clip_on(False)
        axis.grid(visible=False)
        self._sec_raxis = axis
        self.axis_at_side["r_end"] = axis
        return axis

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
        Keep the r-axis tick labels styled by the theme across draws

        The theme styles the tick labels by setting the font on their label
        artists directly, so matplotlib's tick reset -- which `PolarAxes.draw`
        runs on the r-axis -- would otherwise repaint them with its defaults.
        The tick marks are not at risk: their colour, width and length go
        through `set_tick_params`, which the reset preserves. Only the r-axis
        is reset; the theta-axis is not.
        """
        # Wrapping `reset_ticks` restores the styling that lives on the tick
        # artists (rather than in `set_tick_params` state) after every reset.
        # Reading it live from the pre-reset ticks on each call keeps this
        # correct however many resets run: a reset before the theme is applied
        # simply carries the default look forward.
        if self._raxis_tick_style_locked:
            return
        self._raxis_tick_style_locked = True

        axis = self.raxis
        reset_ticks = axis.reset_ticks

        def reset_ticks_and_restyle() -> None:
            # `_copy_tick_props` `update_from`s each label and tick line, so it
            # carries the full look of the pre-reset `majorTicks[0]` /
            # `minorTicks[0]` onto the ticks the reset grows -- the label font
            # included, which is the part `set_tick_params` cannot record.
            major, minor = axis.majorTicks[0], axis.minorTicks[0]
            reset_ticks()
            axis._copy_tick_props(major, axis.majorTicks[0])  # type: ignore
            axis._copy_tick_props(minor, axis.minorTicks[0])  # type: ignore

        axis.reset_ticks = reset_ticks_and_restyle


def _redraw_raxis(axis: p9RadialAxis, renderer: RendererBase) -> None:
    """
    Redraw an r-axis's visible tick marks and labels on top of the geoms

    Each tick's `_tick_side` selects the mark/label pair it occupies: the
    primary r-axis draws the start pair (`tick1line`/`label1`), the secondary
    the end pair (`tick2line`/`label2`) on the opposite side of the shared
    full-circle spoke. Marks draw before labels so a label never sits under
    its own mark.
    """
    for tick in (*axis.majorTicks, *axis.minorTicks):
        if tick._tick_side > 0:  # pyright: ignore[reportAttributeAccessIssue]
            mark, label = tick.tick2line, tick.label2
        else:
            mark, label = tick.tick1line, tick.label1
        if mark.get_visible():
            mark.draw(renderer)
        if label.get_visible():
            label.draw(renderer)


register_projection(p9RadialAxes)

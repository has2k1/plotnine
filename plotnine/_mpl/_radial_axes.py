from __future__ import annotations

from typing import TYPE_CHECKING, cast

import matplotlib.patches as mpatches
import matplotlib.transforms as mtransforms
import numpy as np
from matplotlib import cbook
from matplotlib.projections import register_projection
from matplotlib.projections.polar import (
    PolarAxes,
    RadialAxis,
    ThetaAxis,
    _WedgeBbox,
)

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


class _TightWedgeBbox(_WedgeBbox):
    """
    Wedge bounding box that hugs the sector instead of padding to a square

    matplotlib's `_WedgeBbox` pads the sector's bounding box out to a
    square and centres the wedge in it, which — with a square panel —
    leaves large empty margins around a partial arc. This subclass
    reproduces the tight-box computation but omits that final padding, so
    the sector fills the panel the layout engine has already shaped to the
    same aspect.
    """

    def get_points(self) -> np.ndarray:
        if self._invalid:
            points = self._viewLim.get_points().copy()  # pyright: ignore[reportAttributeAccessIssue]
            points[:, 0] *= 180 / np.pi
            if points[0, 0] > points[1, 0]:
                points[:, 0] = points[::-1, 0]
            points[:, 1] -= self._originLim.y0  # pyright: ignore[reportAttributeAccessIssue]
            points[:, 1] *= 0.5 / points[1, 1]
            width = min(points[1, 1] - points[0, 1], 0.5)
            wedge = mpatches.Wedge(
                self._center,  # pyright: ignore[reportAttributeAccessIssue]
                points[1, 1],
                points[0, 0],
                points[1, 0],
                width=width,
            )
            # `get_extents` evaluates the true curve extents; a plain
            # `update_from_path` would union the wider Bezier control-point
            # hull, which reaches back to the centre and over-widens the
            # box for a narrow donut sector.
            self._points = wedge.get_path().get_extents().get_points().copy()
            self._invalid = 0
        return self._points


class _PanelWedge(mpatches.Wedge):
    """
    Axes-background wedge that fills a wedge-shaped panel undistorted

    `PolarAxes.draw` recomputes the background wedge's centre, radius and
    width on every draw in axes-fraction space, a computation that assumes
    the axes box is square (it takes the radius from the x-scaling of
    `transWedge` alone). In a wedge-shaped, non-square panel that renders the
    background — and the clip path the geoms share — as an ellipse mismatched
    with the data and the spine. This subclass ignores those geometry setters
    and its transform setter, holding a fixed unit wedge whose transform the
    axes sets once to `transWedge + transAxes` — the transform the `polar`
    spine already uses — so the background traces the same arc as the data.

    Blocking `set_transform` is what keeps the geom clip path correct: the
    geoms snapshot the patch's transform *object* when they capture their
    clip, so it must be set once and never replaced. `Axes.clear` would
    otherwise reset it to `transAxes` (a square wedge, which clips the geoms
    to a squashed ellipse). `reshape` sets the real width through the
    base-class setter, bypassing the no-op.
    """

    def set_center(self, center) -> None:
        pass

    def set_radius(self, radius) -> None:
        pass

    def set_width(self, width) -> None:
        pass

    def set_transform(self, t) -> None:
        pass

    def reshape(self, width: float | None) -> None:
        """
        Set the unit-wedge geometry, bypassing the ignored setters
        """
        mpatches.Wedge.set_center(self, (0.5, 0.5))
        mpatches.Wedge.set_radius(self, 0.5)
        mpatches.Wedge.set_width(self, width)


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

    def _gen_axes_patch(self) -> mpatches.Wedge:
        """
        Background wedge that fills a wedge-shaped panel undistorted

        Returns a `_PanelWedge` in place of the stock `Wedge` so the axes
        background (and the clip path the geoms share) traces the same arc
        as the data even when the panel is not square. See `_PanelWedge`.
        Its transform is fixed here to `transWedge + transAxes` (both exist
        by the time the patch is generated) and cannot be replaced, so the
        geoms clip to the true arc. See `_PanelWedge`.
        """
        patch = _PanelWedge((0.5, 0.5), 0.5, 0.0, 360.0)
        mpatches.Wedge.set_transform(
            patch,
            self.transWedge  # pyright: ignore[reportAttributeAccessIssue]
            + self.transAxes,
        )
        return patch

    def _reshape_panel_wedge(self) -> None:
        """
        Restore the background wedge's unit geometry after the square fit

        `_PanelWedge` ignores the square-fit geometry `PolarAxes.draw`
        computes; this sets its true unit-wedge width (the donut hole) so the
        background fills the wedge panel exactly. Its transform is fixed at
        construction and never changes.
        """
        patch = self.patch
        if not isinstance(patch, _PanelWedge):
            return
        rscale = self.yaxis.get_transform()
        rmin, rmax = (
            rscale.transform(self._realViewLim.intervaly)  # pyright: ignore[reportAttributeAccessIssue]
            - rscale.transform(self.get_rorigin())
        ) * self.get_rsign()
        width = min(0.5 * (rmax - rmin) / rmax, 0.5) if rmax else 0.5
        patch.reshape(None if width == 0.5 else width)

    def apply_aspect(self, position=None) -> None:
        """
        Shrink the layout cell to match the tight wedge's aspect, not 1.0

        The stock `PolarAxes.apply_aspect` always shrinks the cell to a
        square (aspect=1.0). That undoes the wedge-shaped cell the layout
        engine assigns from `coord_radial.aspect` for partial arcs. This
        override uses the tight wedge bbox to derive the actual aspect and
        shrinks to that instead, so a full circle still gets a square cell
        and a half-disc gets a 2:1 wide cell.
        """
        if position is None:
            position = self.get_position(original=True)
        trans = self.get_figure(root=False).transSubfigure  # pyright: ignore[reportOptionalMemberAccess]
        bb = mtransforms.Bbox.unit().transformed(trans)
        fig_aspect = bb.height / bb.width
        pts = self.axesLim.get_points()  # pyright: ignore[reportAttributeAccessIssue]
        w = pts[1, 0] - pts[0, 0]
        h = pts[1, 1] - pts[0, 1]
        wedge_aspect = (h / w) if w > 0 else 1.0
        pb = position.frozen()
        pb1 = pb.shrunk_to_aspect(wedge_aspect, pb, fig_aspect)
        anchor = self.get_anchor()
        self._set_position(  # pyright: ignore[reportAttributeAccessIssue]
            pb1.anchored(anchor, pb),  # pyright: ignore[reportArgumentType]
            "active",
        )

    def _set_lim_and_transforms(self) -> None:
        """
        Build the polar transforms, then let the sector fill the panel

        Runs matplotlib's setup, then retypes the square-padding `axesLim`
        bbox in place to `_TightWedgeBbox` so a partial arc hugs the panel
        edges. Retyping the existing object -- rather than rebuilding it and
        the transform stack -- means every transform the base method already
        wired to it (`transData`, the theta/r axis transforms, and the tick
        labels' cached copies of them) recomputes through the tight box
        without any of them going stale. Safe to run at axes-construction
        time: `_TightWedgeBbox` reads only the view/origin limits the base
        method has already set, not any plotnine coordinate state.
        """
        super()._set_lim_and_transforms()  # pyright: ignore[reportAttributeAccessIssue]
        self.axesLim.__class__ = _TightWedgeBbox  # pyright: ignore[reportAttributeAccessIssue]
        self.axesLim.invalidate()  # pyright: ignore[reportAttributeAccessIssue]

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

        # Reshape the background wedge before `super().draw` clips the geoms
        # to it: `PolarAxes.draw` (inside the super call) recomputes the
        # patch assuming a square box, then draws the geoms clipped to that
        # squashed patch in the same call. `_PanelWedge` ignores those
        # geometry setters, so setting the correct unit-wedge geometry and
        # transform here survives the super call and clips the geoms to the
        # true arc.
        self._reshape_panel_wedge()

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
        Return the secondary r-axis, creating it once

        The axis starts with no ticks or labels; the caller sets them via
        `set_ticks` / `set_ticklabels` and registers it in `axis_at_side`
        under the spoke it occupies (opposite the primary). Its tick labels
        are redrawn above geoms on every `draw` call, mirroring the primary
        r-axis behaviour.

        Returns
        -------
        :
            The secondary radial axis.
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

    Only the pair on the axis's active spoke is visible, so redrawing every
    visible mark/label lifts the right one whichever spoke it occupies: the
    primary r-axis moves to the end spoke under `reverse="theta"`, swapping
    with the secondary. Each mark draws before its label so a label never
    sits under its own mark.
    """
    for tick in (*axis.majorTicks, *axis.minorTicks):
        for mark, label in (
            (tick.tick1line, tick.label1),
            (tick.tick2line, tick.label2),
        ):
            if mark.get_visible():
                mark.draw(renderer)
            if label.get_visible():
                label.draw(renderer)


register_projection(p9RadialAxes)

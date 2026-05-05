from __future__ import annotations

from typing import TYPE_CHECKING

from matplotlib import artist
from matplotlib.patches import FancyBboxPatch, Rectangle
from matplotlib.transforms import Bbox

from plotnine._mpl.utils import rel_position

if TYPE_CHECKING:
    from plotnine.typing import StripPosition

    from .text import StripText


# We subclass because we want to learn the size and location
# of the box when the layout manager is running.
# With MPLs default text & boxpatch, the patch gets its
# dimension information at draw time.


class StripTextPatch(FancyBboxPatch):
    """
    Strip text background box
    """

    text: StripText
    """
    The text artists that is wrapped by this box
    """

    position: StripPosition
    """
    The position of the strip_text associated with this patch
    """

    expand: float = 1
    """
    Factor by which to expand the thickness of this patch.

    This value is used by the layout manager to increase the breadth
    of the narrower strip_backgrounds.
    """

    def __init__(self, text: StripText):
        super().__init__(
            # The position, width and height are determine in
            # .get_window_extent.
            (0, 0),
            width=1,
            height=1,
            boxstyle="square, pad=0",
            clip_on=False,
            zorder=2.2,
        )

        self.text = text
        self.position = text.draw_info.position

    def get_window_extent(self, renderer=None):
        """
        Location & dimensions of the box in display coordinates
        """
        info = self.text.draw_info
        m = info.margin

        # bboxes in display space
        text_bbox = self.text.get_window_extent(renderer)
        ax_bbox = info.ax.bbox.frozen()

        # line height in display space
        line_height = self.text._line_height(renderer)

        # Convert the bottom left coordinates of the patch  from
        # transAxes to display space. We are not justifying the patch
        # within the axes so we use 0 for the lengths, this gives us
        # a patch that starts at the edge of the axes and not one that
        # ends at the edge
        x0 = rel_position(info.bg_x, 0, ax_bbox.x0, ax_bbox.x1)
        y0 = rel_position(info.bg_y, 0, ax_bbox.y0, ax_bbox.y1)

        # info.bg_width and info.bg_height are in axes space
        # so they are a scaling factor
        if info.position == "top":
            width = ax_bbox.width * info.bg_width
            height = text_bbox.height + ((m.b + m.t) * line_height)
            height *= self.expand
            y0 += height * info.strip_align
        else:
            height = ax_bbox.height * info.bg_height
            width = text_bbox.width + ((m.l + m.r) * line_height)
            width *= self.expand
            x0 += width * info.strip_align

        return Bbox.from_bounds(x0, y0, width, height)

    @artist.allow_rasterization
    def draw(self, renderer):
        """
        Draw patch
        """
        # The geometry of the patch is determined by its rectangular bounds,
        # this is also its "window_extent". As the extent value is in
        # display units, we don't need a transform.
        bbox = self.get_window_extent(renderer)
        self.set_bounds(bbox.bounds)
        self.set_transform(None)
        return super().draw(renderer)


class InsideStrokedRectangle(Rectangle):
    """
    A rectangle whose stroke is fully contained within it
    """

    @artist.allow_rasterization
    def draw(self, renderer):
        """
        Draw stroking at 2·lw and clipping to the rectangle's own boundary

        The outer half of the stroke is removed by the clip, leaving exactly
        `lw` of stroke fully inside the rectangle, with the visible outer edge
        of the stroke on the original boundary. This is transform-agnostic
        (works under data, axes, identity, and DrawingArea transforms) and
        idempotent across redraws.
        """
        lw = self.get_linewidth()
        if lw <= 0:
            return super().draw(renderer)

        saved_clip_path = self.get_clip_path()
        saved_clip_on = self.get_clip_on()

        # Dash lengths track the linewidth: matplotlib stores the dash
        # pattern as multipliers and scales them whenever set_linewidth is
        # called. Doubling lw below would therefore stretch the dashes 2x.
        # Snapshot the pattern at the user's lw now and write it back after
        # the doubling so the dashes render at their requested length.
        original_dash_pattern = self._dash_pattern
        try:
            self.set_linewidth(2 * lw)
            self._dash_pattern = original_dash_pattern
            self.set_clip_path(self.get_path(), self.get_transform())
            self.set_clip_on(True)
            self.set_snap(False)
            super().draw(renderer)
        finally:
            self.set_linewidth(lw)
            self.set_clip_path(saved_clip_path)
            self.set_clip_on(saved_clip_on)

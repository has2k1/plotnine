from __future__ import annotations

from matplotlib import artist
from matplotlib.patches import Rectangle


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

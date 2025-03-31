from __future__ import annotations

from typing import TYPE_CHECKING

from matplotlib.text import Text

from .patches import StripTextPatch
from .utils import bbox_in_axes_space, rel_position

if TYPE_CHECKING:
    from matplotlib.backend_bases import RendererBase

    from plotnine.iapi import strip_draw_info
    from plotnine.typing import HorizontalJustification, VerticalJustification


class StripText(Text):
    """
    Strip Text
    """

    draw_info: strip_draw_info
    patch: StripTextPatch

    def __init__(self, info: strip_draw_info):
        kwargs = {
            "rotation": info.rotation,
            "transform": info.ax.transAxes,
            "clip_on": False,
            "zorder": 3.3,
        }

        super().__init__(
            info.x,
            info.y,
            info.label,
            **kwargs,
        )
        self.draw_info = info
        self.patch = StripTextPatch(self)

    # TODO: Move these _justify methods to the layout manager
    # We need to first make sure that the patch has the final size during
    # layout computation. Right now, the final size is calculated during
    # draw (in these justify methods)
    def _justify_horizontally(self, renderer):
        """
        Justify the text along the strip_background
        """
        info = self.draw_info
        lookup: dict[HorizontalJustification, float] = {
            "left": 0.0,
            "center": 0.5,
            "right": 1.0,
        }
        rel = lookup.get(info.ha, 0.5) if isinstance(info.ha, str) else info.ha
        patch_bbox = bbox_in_axes_space(self.patch, info.ax, renderer)
        text_bbox = bbox_in_axes_space(self, info.ax, renderer)
        l, b, w, h = info.x, info.y, info.box_width, patch_bbox.height
        b = b + patch_bbox.height * info.strip_align
        x = rel_position(rel, text_bbox.width, patch_bbox.x0, patch_bbox.x1)
        y = b + h / 2
        self.set_horizontalalignment("left")
        self.patch.set_bounds(l, b, w, h)
        self.set_position((x, y))

    def _justify_vertically(self, renderer):
        """
        Justify the text along the strip_background
        """
        # Note that the strip text & background and horizontal but
        # rotated to appear vertical. So we really are still justifying
        # horizontally.
        info = self.draw_info
        lookup: dict[VerticalJustification, float] = {
            "bottom": 0.0,
            "center": 0.5,
            "top": 1.0,
        }
        rel = lookup.get(info.va, 0.5) if isinstance(info.va, str) else info.va
        patch_bbox = bbox_in_axes_space(self.patch, info.ax, renderer)
        text_bbox = bbox_in_axes_space(self, info.ax, renderer)
        l, b, w, h = info.x, info.y, patch_bbox.width, info.box_height
        l = l + patch_bbox.width * info.strip_align
        x = l + w / 2
        y = rel_position(rel, text_bbox.height, patch_bbox.y0, patch_bbox.y1)
        self.set_horizontalalignment("right")  # 90CW right means bottom
        self.patch.set_bounds(l, b, w, h)
        self.set_position((x, y))

    def draw(self, renderer: RendererBase):
        if not self.get_visible():
            return

        # expand strip_text patch to contain the text
        self.patch.update_position_size(renderer)

        # Align patch across the edge of the panel
        if self.draw_info.position == "top":
            self._justify_horizontally(renderer)
        else:  # "right"
            self._justify_vertically(renderer)

        self.patch.set_transform(self.draw_info.ax.transAxes)
        self.patch.set_mutation_scale(0)

        # Put text in center of patch
        self.set_rotation_mode("anchor")
        self.set_verticalalignment("center_baseline")

        # Draw spatch
        self.patch.draw(renderer)
        return super().draw(renderer)

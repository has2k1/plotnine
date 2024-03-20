from __future__ import annotations

import typing

from matplotlib.text import Text

from .patches import StripTextPatch
from .utils import bbox_in_axes_space

if typing.TYPE_CHECKING:
    from matplotlib.backend_bases import RendererBase

    from plotnine.iapi import strip_draw_info


class StripText(Text):
    """
    Strip Text
    """

    draw_info: strip_draw_info
    patch: StripTextPatch

    def __init__(self, info: strip_draw_info):
        kwargs = {
            "ha": info.ha,
            "va": info.va,
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

    def draw(self, renderer: RendererBase):
        if not self.get_visible():
            return

        info = self.draw_info
        # "fill up" spatch to contain the text
        self.patch.update_position_size(renderer)

        # Get bbox of spatch in transAxes space
        patch_bbox = bbox_in_axes_space(self.patch, info.ax, renderer)

        # Align patch across the edge of the panel
        if info.position == "top":
            l, b, w, h = info.x, info.y, info.box_width, patch_bbox.height
            b = b + patch_bbox.height * info.strip_align
        else:  # "right"
            l, b, w, h = info.x, info.y, patch_bbox.width, info.box_height
            l = l + patch_bbox.width * info.strip_align

        self.patch.set_bounds(l, b, w, h)
        self.patch.set_transform(info.ax.transAxes)
        self.patch.set_mutation_scale(0)

        # Put text in center of patch
        self._x = l + w / 2
        self._y = b + h / 2

        # "anchor" aligns before rotation so the right-strip get properly
        # centered text
        self.set_rotation_mode("anchor")
        self.set_horizontalalignment("center")  # right-strip
        self.set_verticalalignment("center_baseline")  # top-strip

        # Draw spatch
        self.patch.draw(renderer)
        return super().draw(renderer)

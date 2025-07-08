from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING

from matplotlib import artist
from matplotlib.text import Text

from plotnine._utils import ha_as_float, va_as_float

from .patches import StripTextPatch
from .utils import bbox_in_axes_space, rel_position

if TYPE_CHECKING:
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
            "rotation": info.rotation,
            "transform": info.ax.transAxes,
            "clip_on": False,
            "zorder": 3.3,
            # Since the text can be rotated, it is simpler to anchor it at
            # the center, align it, then do the rotation. Vertically,
            # center_baseline places the text in the visual center, but
            # only if it is one line. For multiline text, we are better
            # off with plain center.
            "ha": "center",
            "va": "center_baseline" if info.is_oneline else "center",
            "rotation_mode": "anchor",
        }

        super().__init__(0, 0, info.label, **kwargs)
        self.draw_info = info
        self.patch = StripTextPatch(self)

    # TODO: This should really be part of the unit conversions in the
    # margin class.
    @lru_cache(2)
    def _line_height(self, renderer) -> float:
        """
        The line height in display space of the text on the canvas
        """
        # Text string, (width, height), x, y
        parts: list[tuple[str, tuple[float, float], float, float]]

        try:
            # matplotlib.Text._get_layout is a private API and we cannot
            # tell how using it may fail in the future.
            _, parts, _ = self._get_layout(renderer)  # pyright: ignore[reportAttributeAccessIssue]
        except Exception:
            from warnings import warn

            from plotnine.exceptions import PlotnineWarning

            # The canvas height is nearly always bigger than the stated
            # fontsize. 1.36 is a good multiplication factor obtained by
            # some rough exploration
            f = 1.36
            size = self.get_fontsize()
            height = round(size * f) if isinstance(size, int) else 14
            warn(
                f"Could not calculate line height for {self.get_text()}. "
                "Using an estimate, please let us know about this at "
                "https://github.com/has2k1/plotnine/issues",
                PlotnineWarning,
            )
        else:
            # The the text has multiple lines, we use the maximum height
            # of anyone single line.
            height = max([p[1][1] for p in parts])

        return height

    def _set_position(self, renderer):
        """
        Set the postion of the text within the strip_background
        """
        # We have to two premises that depend on each other:
        #
        #    1. The breadth of the strip_background grows to accomodate
        #       the strip_text.
        #    2. The strip_text is justified within the strip_background.
        #
        # From these we note that the strip_background does not need the
        # position of the strip_text, but it needs its size. Therefore
        # we implement StripTextPatch.get_window_extent can use
        # StripText.get_window_extent, peeking only at the size.
        #
        # And we implement StripText._set_position_* to use
        # StripTextPatch.get_window_extent and make the calculations in
        # both methods independent.
        if self.draw_info.position == "top":
            self._set_position_top(renderer)
        else:  # "right"
            self._set_position_right(renderer)

    def _set_position_top(self, renderer):
        """
        Set position of the text within the top strip_background
        """
        info = self.draw_info
        ha, va, ax, m = info.ha, info.va, info.ax, info.margin

        rel_x, rel_y = ha_as_float(ha), va_as_float(va)
        patch_bbox = bbox_in_axes_space(self.patch, ax, renderer)
        text_bbox = bbox_in_axes_space(self, ax, renderer)

        # line_height and margins in axes space
        line_height = self._line_height(renderer) / ax.bbox.height

        x = (
            # Justify horizontally within the strip_background
            rel_position(
                rel_x,
                text_bbox.width + (line_height * (m.l + m.r)),
                patch_bbox.x0,
                patch_bbox.x1,
            )
            + (m.l * line_height)
            + text_bbox.width / 2
        )
        # Setting the y position based on the bounding box is wrong
        y = (
            rel_position(
                rel_y,
                text_bbox.height,
                patch_bbox.y0 + m.b * line_height,
                patch_bbox.y1 - m.t * line_height,
            )
            + text_bbox.height / 2
        )
        self.set_position((x, y))

    def _set_position_right(self, renderer):
        """
        Set position of the text within the bottom strip_background
        """
        info = self.draw_info
        ha, va, ax, m = info.ha, info.va, info.ax, info.margin

        # bboxes in axes space
        patch_bbox = bbox_in_axes_space(self.patch, ax, renderer)
        text_bbox = bbox_in_axes_space(self, ax, renderer)

        # line_height in axes space
        line_height = self._line_height(renderer) / ax.bbox.width

        rel_x, rel_y = ha_as_float(ha), va_as_float(va)

        x = (
            rel_position(
                rel_x,
                text_bbox.width,
                patch_bbox.x0 + m.l * line_height,
                patch_bbox.x1 - m.r * line_height,
            )
            + text_bbox.width / 2
        )
        y = (
            # Justify vertically within the strip_background
            rel_position(
                rel_y,
                text_bbox.height + ((m.b + m.t) * line_height),
                patch_bbox.y0,
                patch_bbox.y1,
            )
            + (m.b * line_height)
            + text_bbox.height / 2
        )
        self.set_position((x, y))

    @artist.allow_rasterization
    def draw(self, renderer: RendererBase):
        """
        Draw text along with the patch
        """
        if not self.get_visible():
            return

        self._set_position(renderer)
        self.patch.draw(renderer)
        return super().draw(renderer)

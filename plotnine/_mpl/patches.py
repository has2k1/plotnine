from __future__ import annotations

from typing import TYPE_CHECKING

from matplotlib import artist
from matplotlib.patches import FancyBboxPatch, Rectangle
from matplotlib.text import _get_textbox  # type: ignore
from matplotlib.transforms import Affine2D

if TYPE_CHECKING:
    from matplotlib.backend_bases import RendererBase

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

    # The text artists that is wrapped by this box
    text: StripText
    position: StripPosition
    _update = False

    def __init__(self, text: StripText):
        boxstyle = f"square, pad={text.draw_info.strip_text_margin}"

        super().__init__(
            (0, 0), 1, 1, boxstyle=boxstyle, clip_on=False, zorder=2.2
        )

        self.text = text
        self.position = text.draw_info.position

    def update_position_size(self, renderer: RendererBase):
        """
        Update the location and the size of the bbox.
        """
        if self._update:
            return

        text = self.text
        posx, posy = text.get_transform().transform((text._x, text._y))
        x, y, w, h = _get_textbox(text, renderer)

        self.set_bounds(0.0, 0.0, w, h)
        self.set_transform(
            Affine2D()
            .rotate_deg(text.get_rotation())
            .translate(posx + x, posy + y)
        )
        fontsize_in_pixel = renderer.points_to_pixels(
            text.get_size()  # type: ignore
        )
        self.set_mutation_scale(fontsize_in_pixel)  # type: ignore
        self._update = True

    def get_window_extent(self, renderer=None):
        """
        Location & dimensions of the box
        """
        if renderer:
            self.update_position_size(renderer)
        return super().get_window_extent(renderer)


class InsideStrokedRectangle(Rectangle):
    """
    A rectangle whose stroked is fully contained within it
    """

    @artist.allow_rasterization
    def draw(self, renderer):
        """
        Draw with the bounds of the rectangle adjusted to accomodate the stroke
        """
        x, y = self.xy
        w, h = self.get_width(), self.get_height()
        lw = self.get_linewidth()
        self.set_bounds((x + lw / 2), (y + lw / 2), (w - lw), (h - lw))
        super().draw(renderer)

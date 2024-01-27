from __future__ import annotations

from matplotlib.offsetbox import AuxTransformBox, DrawingArea
from matplotlib.patches import bbox_artist as mbbox_artist
from matplotlib.transforms import Affine2D

from .patches import InsideStrokedRectangle

DEBUG = False


# for debugging use
def _bbox_artist(*args, **kwargs):
    if DEBUG:
        mbbox_artist(*args, **kwargs)


class ColoredDrawingArea(DrawingArea):
    """
    A Drawing Area with a background color
    """

    def __init__(
        self,
        width: float,
        height: float,
        xdescent=0.0,
        ydescent=0.0,
        clip=True,
        color="none",
    ):
        super().__init__(width, height, xdescent, ydescent, clip=clip)

        self.patch = InsideStrokedRectangle(
            (0, 0),
            width=width,
            height=height,
            facecolor=color,
            edgecolor="None",
            linewidth=0,
            antialiased=False,
        )
        self.add_artist(self.patch)


# Fix AuxTransformBox, Adds a dpi_transform
# See https://github.com/matplotlib/matplotlib/pull/7344
class DPICorAuxTransformBox(AuxTransformBox):
    """
    DPI Corrected AuxTransformBox
    """

    def __init__(self, aux_transform):
        super().__init__(aux_transform)
        self.dpi_transform = Affine2D()
        self._dpi_corrected = False

    def get_transform(self):
        """
        Return the :class:`~matplotlib.transforms.Transform` applied
        to the children
        """
        return (
            self.aux_transform
            + self.dpi_transform
            + self.ref_offset_transform
            + self.offset_transform
        )

    def _correct_dpi(self, renderer):
        if not self._dpi_corrected:
            dpi_cor = renderer.points_to_pixels(1.0)
            self.dpi_transform.clear()
            self.dpi_transform.scale(dpi_cor, dpi_cor)
            self._dpi_corrected = True

    def get_bbox(self, renderer):
        self._correct_dpi(renderer)
        return super().get_bbox(renderer)

    def draw(self, renderer):
        """
        Draw the children
        """
        self._correct_dpi(renderer)
        for c in self.get_children():
            c.draw(renderer)

        _bbox_artist(self, renderer, fill=False, props=dict(pad=0.0))
        self.stale = False

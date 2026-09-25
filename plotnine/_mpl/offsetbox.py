from __future__ import annotations

from typing import TYPE_CHECKING, cast

from matplotlib.offsetbox import (
    AnchoredOffsetbox,
    AuxTransformBox,
    DrawingArea,
    PackerBase,
)
from matplotlib.patches import bbox_artist as mbbox_artist
from matplotlib.transforms import Affine2D, Bbox

from .patches import InsideStrokedRectangle

if TYPE_CHECKING:
    from collections.abc import Sequence

    from matplotlib.artist import Artist
    from matplotlib.backend_bases import RendererBase
    from matplotlib.offsetbox import OffsetBox

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
            edgecolor="none",
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
        Return the [](`~matplotlib.transforms.Transform`) applied
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


class FlexibleAnchoredOffsetbox(AnchoredOffsetbox):
    """
    An AnchoredOffsetbox that accepts x, y location
    """

    def __init__(self, xy_loc: tuple[float, float] = (0.5, 0.5), **kwargs):
        if "loc" in kwargs:
            raise ValueError(
                "FlexibleAnchoredOffsetbox does not use the 'loc' parameter"
            )

        super().__init__(loc="center", **kwargs)
        self.xy_loc = xy_loc

    def get_offset(self, bbox, renderer):  # type: ignore
        pad = self.borderpad * renderer.points_to_pixels(
            self.prop.get_size_in_points()
        )
        parentbbox = self.get_bbox_to_anchor()
        _bbox = Bbox.from_bounds(0, 0, bbox.width, bbox.height)
        container = parentbbox.padded(-pad)
        x0, y0 = _bbox.anchored(self.xy_loc, container=container).p0
        return x0 - bbox.x0, y0 - bbox.y0


class OffsetPacker(PackerBase):
    """
    Container for children placed at fixed point offsets

    Numeric dimensions set a minimum extent from the origin. The bounds expand
    to include each visible child's measured extent without shifting its
    offset. A `None` dimension uses only the child bounds.
    """

    def __init__(
        self,
        width: float | None,
        height: float | None,
        children: Sequence[Artist],
        offsets: Sequence[tuple[float, float]],
    ) -> None:
        super().__init__(children=list(children))
        self._box_width = width
        self._box_height = height
        self._child_offsets = offsets

    def _get_bbox_and_child_offsets(
        self, renderer: RendererBase
    ) -> tuple[Bbox, list[tuple[float, float]]]:
        scale = cast("float", renderer.points_to_pixels(1.0))
        offsets = [(x * scale, y * scale) for x, y in self._child_offsets]
        visible = [
            (child, offset)
            for child, offset in zip(self.get_children(), offsets)
            if child.get_visible()
        ]
        child_boxes = [
            cast("OffsetBox", child).get_bbox(renderer).translated(x, y)
            for child, (x, y) in visible
        ]
        contents = (
            Bbox.union(child_boxes)
            if child_boxes
            else Bbox.from_bounds(0, 0, 0, 0)
        )
        x0 = (
            min(0, contents.x0) if self._box_width is not None else contents.x0
        )
        y0 = (
            min(0, contents.y0)
            if self._box_height is not None
            else contents.y0
        )
        x1 = (
            max(self._box_width * scale, contents.x1)
            if self._box_width is not None
            else contents.x1
        )
        y1 = (
            max(self._box_height * scale, contents.y1)
            if self._box_height is not None
            else contents.y1
        )
        return (
            Bbox.from_extents(x0, y0, x1, y1),
            [offset for _, offset in visible],
        )

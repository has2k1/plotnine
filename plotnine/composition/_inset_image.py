from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING

import numpy as np
from PIL.Image import Image as PILImage

from ..themes.theme import theme

if TYPE_CHECKING:
    from matplotlib.figure import Figure
    from matplotlib.patches import Rectangle
    from matplotlib.transforms import Bbox

    from plotnine._mpl.figure import p9Figure

    from ..ggplot import ggplot
    from ..themes.theme import theme as theme_type


class _InsetImage:
    """
    A raster image rendered inside an `inset_element`'s bounding box

    The image keeps its intrinsic aspect ratio — when the bbox does
    not match, the image is letterboxed with transparent padding on
    the two opposing edges so it stays centred.

    Theming the inset (`inset_element(...) + theme(...)`) draws a
    background rectangle around the image; only `plot_background`
    is honored, and it styles that rectangle's fill and border.
    """

    # The host figure this inset renders into.
    figure: p9Figure
    # Theme that styles the background rectangle.
    theme: theme_type
    # Background rectangle drawn around the image.
    patch: Rectangle

    # Bbox that defines the position and size of the final image
    # artist. When the original image is mapped onto the figure,
    # this bbox sets where on the figure it lands and how big it is.
    _frac_bbox: Bbox

    def __init__(self, image: PILImage | np.ndarray):
        from matplotlib.transforms import Bbox

        self._image = image
        self._image_size = _image_size(image)  # (W, H) px
        self._frac_bbox = Bbox.unit()
        self.theme = theme()

    def __add__(self, other: object) -> _InsetImage:
        if not isinstance(other, theme):
            return NotImplemented

        new = deepcopy(self)
        new.theme = (new.theme or theme()) + other
        return new

    def _setup(self, parent: ggplot):
        self.figure = parent.figure

    def _arrange_in_box(
        self, left: float, bottom: float, right: float, top: float
    ):
        """
        Place the image inside the given box, preserving aspect ratio

        The image is letterboxed — centered inside the box with
        transparent padding on the two opposing edges — so its
        intrinsic aspect ratio survives. The background rectangle
        tracks the same fitted box.

        Parameters
        ----------
        left, bottom, right, top :
            Fractional figure-coordinates of the box assigned to this
            inset by `inset_element.align_to`.
        """
        l, b, r, t = _fit_aspect(
            left, bottom, right, top, self._image_size, self.figure
        )
        w, h = r - l, t - b
        self._frac_bbox.bounds = (l, b, w, h)  # pyright: ignore[reportAttributeAccessIssue]
        self.patch.set_bounds(l, b, w, h)

    def draw(self):
        from matplotlib.image import BboxImage
        from matplotlib.transforms import TransformedBbox

        image_artist = BboxImage(
            TransformedBbox(self._frac_bbox, self.figure.transFigure)
        )
        image_artist.set_data(np.asarray(self._image))
        self.figure.add_artist(image_artist)

        self.theme._setup(self)  # pyright: ignore[reportArgumentType]
        self._draw_plot_background()
        self.theme.apply()

    def _draw_plot_background(self):
        from matplotlib.patches import Rectangle

        self.patch = self.figure.add_artist(
            Rectangle(
                (0, 0),
                1,
                1,
                facecolor="none",
                transform=self.figure.transFigure,
            )
        )
        self.theme.targets.plot_background = self.patch


def _image_size(obj: PILImage | np.ndarray) -> tuple[int, int]:
    """
    Return the (width, height) of a PIL image or ndarray in pixels
    """
    if isinstance(obj, PILImage):
        return obj.size  # PIL exposes (W, H)

    arr = np.asarray(obj)
    h, w = arr.shape[:2]  # ndarray is HWC or HW
    return w, h


def _fit_aspect(
    left: float,
    bottom: float,
    right: float,
    top: float,
    image_size: tuple[int, int],
    fig: Figure,
) -> tuple[float, float, float, float]:
    """
    Shrink the user's bbox to the largest centered sub-bbox with the
    image's intrinsic aspect ratio
    """
    # figure size in px
    W, H = fig.bbox.size

    # box size in px
    box_w = (right - left) * W
    box_h = (top - bottom) * H

    img_w, img_h = image_size
    img_aspect = img_w / img_h
    box_aspect = box_w / box_h

    if img_aspect > box_aspect:
        # Wider than the box: fit width, letterbox vertically
        new_box_h = box_w / img_aspect
        pad_frac = (box_h - new_box_h) / 2 / H
        return left, bottom + pad_frac, right, top - pad_frac

    # Taller (or equal): fit height, letterbox horizontally
    new_box_w = box_h * img_aspect
    pad_frac = (box_w - new_box_w) / 2 / W
    return left + pad_frac, bottom, right - pad_frac, top

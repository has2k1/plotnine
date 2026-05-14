from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING, Literal

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

    AnchorName = Literal[
        "center",
        "top",
        "right",
        "bottom",
        "left",
        "top-left",
        "top-right",
        "bottom-left",
        "bottom-right",
    ]
    Anchor = AnchorName | tuple[float, float]


class _InsetImage:
    """
    A raster image rendered inside an `inset_element`'s bounding box

    The image keeps its intrinsic aspect ratio — when the bbox does
    not match, the image is letterboxed with transparent padding on
    the two opposing edges. The `anchor` parameter chooses where the
    image sits inside the bbox (centered by default).

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

    # Where the image sits inside the user's bbox when its aspect
    # ratio doesn't match.
    _anchor: tuple[float, float]

    def __init__(
        self,
        image: PILImage | np.ndarray,
        *,
        anchor: Anchor = "center",
    ):
        from matplotlib.transforms import Bbox

        self._image = image
        self._image_size = _image_size(image)  # (W, H) px
        self._frac_bbox = Bbox.unit()
        self._anchor = _resolve_anchor(anchor)
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

        The image is letterboxed inside the box with transparent
        padding on the two opposing edges, positioned by the
        configured `anchor`. The background rectangle wraps the full
        user bbox (the letterbox envelope), so a themed fill or
        border surrounds the entire requested region — not just the
        fitted image.

        Parameters
        ----------
        left, bottom, right, top :
            Fractional figure-coordinates of the box assigned to this
            inset by `inset_element.align_to`.
        """
        l, b, r, t = _fit_aspect(
            left,
            bottom,
            right,
            top,
            self._image_size,
            self.figure,
            anchor=self._anchor,
        )
        self._frac_bbox.bounds = (l, b, r - l, t - b)  # pyright: ignore[reportAttributeAccessIssue]
        self.patch.set_bounds(left, bottom, right - left, top - bottom)

    def draw(self):
        from matplotlib.image import BboxImage
        from matplotlib.transforms import TransformedBbox

        # Background first so its fill sits behind the image — the
        # letterbox.
        self.theme._setup(self)  # pyright: ignore[reportArgumentType]
        self._draw_plot_background()

        image_artist = BboxImage(
            TransformedBbox(self._frac_bbox, self.figure.transFigure)
        )
        image_artist.set_data(np.asarray(self._image))
        self.figure.add_artist(image_artist)

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


# Named anchors → (h, v) fractions in [0, 1]², where `h = 0`
# aligns the image to the bbox's left edge / `h = 1` to the right,
# and `v = 0` aligns to the bottom / `v = 1` to the top.
_ANCHOR_FRACTIONS: dict[str, tuple[float, float]] = {
    "center": (0.5, 0.5),
    "top": (0.5, 1.0),
    "top-right": (1.0, 1.0),
    "right": (1.0, 0.5),
    "bottom-right": (1.0, 0.0),
    "bottom": (0.5, 0.0),
    "bottom-left": (0.0, 0.0),
    "left": (0.0, 0.5),
    "top-left": (0.0, 1.0),
}


def _resolve_anchor(anchor: Anchor) -> tuple[float, float]:
    """
    Normalise an anchor spec to a (h, v) tuple in [0, 1]²

    Accepts a named anchor (e.g. `"top-right"`) or a numeric
    `(h, v)` tuple. Raises `ValueError` on unknown names or
    out-of-range tuple values.
    """
    if isinstance(anchor, str):
        try:
            return _ANCHOR_FRACTIONS[anchor]
        except KeyError:
            names = ", ".join(repr(k) for k in _ANCHOR_FRACTIONS)
            raise ValueError(
                f"Unknown anchor {anchor!r}. Expected one of: "
                f"{names}, or a (h, v) tuple in [0, 1]²."
            ) from None
    try:
        h, v = anchor
    except (TypeError, ValueError):
        raise ValueError(
            f"Anchor must be a name or (h, v) tuple, got {anchor!r}."
        ) from None
    if not (0.0 <= h <= 1.0 and 0.0 <= v <= 1.0):
        raise ValueError(
            f"Anchor tuple values must lie in [0, 1], got ({h}, {v})."
        )
    return float(h), float(v)


def _fit_aspect(
    left: float,
    bottom: float,
    right: float,
    top: float,
    image_size: tuple[int, int],
    fig: Figure,
    anchor: tuple[float, float] = (0.5, 0.5),
) -> tuple[float, float, float, float]:
    """
    Shrink the user's bbox to the largest sub-bbox with the image's
    intrinsic aspect ratio, positioned by `anchor`

    `anchor` defaults to `"center"` (image centered, padding split
    50/50 on the short axis). Named anchors map to corners and edges
    of the bbox; a `(h, v)` tuple in [0, 1]² sets the anchor
    point directly, where `h = 0` aligns the image to the bbox's
    left edge / `h = 1` to the right, and `v = 0` to the bottom /
    `v = 1` to the top.
    """
    # figure size in px
    W, H = fig.bbox.size

    # box size in px
    box_w = (right - left) * W
    box_h = (top - bottom) * H

    img_w, img_h = image_size
    img_aspect = img_w / img_h
    box_aspect = box_w / box_h

    h, v = anchor

    if img_aspect > box_aspect:
        # Wider than the box: fit width, letterbox vertically
        new_box_h = box_w / img_aspect
        pad = (box_h - new_box_h) / H
        return left, bottom + v * pad, right, top - (1 - v) * pad

    # Taller (or equal): fit height, letterbox horizontally
    new_box_w = box_h * img_aspect
    pad = (box_w - new_box_w) / W
    return left + h * pad, bottom, right - (1 - h) * pad, top

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal

from ._inset_image import _InsetImage

if TYPE_CHECKING:
    import numpy as np
    from matplotlib.figure import Figure
    from PIL.Image import Image as PILImage

    from ..ggplot import ggplot
    from ._compose import Compose
    from ._inset_image import Anchor


@dataclass
class inset_element:
    """
    Place a plot as an inset within another plot

    By default the inset is rendered on top of the host (`on_top=True`).
    With `on_top=False` it is rendered behind the host's panel and
    labels but above the host's `plot_background`. Adding an
    `inset_element` to a composition attaches it to the most recently
    added plot in that composition.

    Parameters
    ----------
    obj :
        The object to render as an inset. One of:

        - `ggplot` or `Compose` — full plot pipeline.
        - `PIL.Image.Image` or `numpy.ndarray` — raster image. The
          image is letterboxed inside the user's bbox so its aspect
          ratio is preserved.
    left, bottom, right, top :
        Bounding box of the inset as fractional coordinates in the
        range `[0, 1]`, relative to the host region selected by
        `align_to`. The bottom-left corner of that region is
        `(0, 0)` and the top-right is `(1, 1)`.
    align_to :
        Which region of the host plot the bounding box is relative to:

        - `"panel"` — the data area only (default).
        - `"plot"`  — the panel plus axes, labels, titles, captions
           and legends
        - `"full"`  — everything the host plot occupies plus plot margin
    on_top :
        When `True` (default) the inset paints above the host plot.
        When `False`, the inset paints between the host's
        `plot_background` and the rest of the host (panel, titles,
        legends, ...), so the host's panel area covers the inset.
        Useful for backdrops, decorations, or branding that should
        look like part of the page rather than an overlay.
    anchor :
        Where to anchor the image inside the user's bbox when its
        aspect ratio doesn't match. One of `"center"` (default),
        `"top"`, `"top-right"`, `"right"`, `"bottom-right"`,
        `"bottom"`, `"bottom-left"`, `"left"`, `"top-left"`,
        or a `(h, v)` tuple in [0, 1]² with `h = 0` left / `h = 1`
        right and `v = 0` bottom / `v = 1` top. Only meaningful for
        image insets; plot / composition insets fill the entire area by
        resizing without constraining the aspect ratio, so the anchor
        has no effect.

    Notes
    -----
    `figure_size` and `dpi` set on the inset's theme are ignored. The
    inset shares the host's figure, so these values come from the host
    theme. The canvas size of the inset is determined by the bounding
    box and the area it is `align_to`.

    For image insets, `inset_element(...) + theme(...)` draws a
    sibling rectangle around the image; only `plot_background` is
    honored today.

    Examples
    --------
    Composed with a host plot:

    >>> p = ggplot(mtcars, aes("wt", "mpg")) + geom_point()  # doctest: +SKIP
    >>> p + inset_element(p, 0.6, 0.6, 1, 1)                 # doctest: +SKIP

    Image inset with a black border:

    >>> from PIL import Image                                # doctest: +SKIP
    >>> p + (                                                # doctest: +SKIP
    ...     inset_element(Image.open("logo.png"), 0.7, 0.7, 1, 1)
    ...     + theme(plot_background=element_rect(color="black", size=1))
    ... )
    """

    obj: ggplot | Compose | PILImage | np.ndarray | _InsetImage
    left: float
    bottom: float
    right: float
    top: float
    align_to: Literal["panel", "plot", "full"] = "panel"
    on_top: bool = True
    anchor: Anchor = "center"

    def __post_init__(self):
        import numpy as np
        from PIL.Image import Image as PILImage

        from ..ggplot import ggplot
        from ._compose import Compose

        if isinstance(self.obj, (ggplot, Compose)):
            pass
        elif isinstance(self.obj, (PILImage, np.ndarray)):
            self.obj = _InsetImage(self.obj, anchor=self.anchor)
        else:
            raise TypeError(
                "inset_element requires a ggplot, Compose, PIL image, "
                f"or ndarray, got {type(self.obj).__name__!r}."
            )

        if not 0.0 <= self.left < self.right <= 1.0:
            raise ValueError(
                "inset_element requires 0.0 <= left < right <= 1.0, got "
                f"left={self.left!r}, right={self.right!r}."
            )

        if not 0.0 <= self.bottom < self.top <= 1.0:
            raise ValueError(
                "inset_element requires 0.0 <= bottom < top <= 1.0, got "
                f"bottom={self.bottom!r}, top={self.top!r}."
            )

    def _setup(self, parent: ggplot):
        """
        Receive the host figure and figure-owner-only theme props

        Parameters
        ----------
        parent :
            The host plot whose figure this inset adopts.
        """
        from ..ggplot import ggplot
        from ._compose import Compose

        if isinstance(self.obj, (ggplot, Compose)):
            self.obj.figure = parent.figure
            self.obj.theme._inherit_figure_props(parent.theme)
        elif isinstance(self.obj, _InsetImage):
            self.obj._setup(parent)

    def __add__(self, other: object) -> inset_element:
        """
        Attach a theme to this inset

        Returns a new `inset_element` with the theme folded into the
        underlying `obj`. For `ggplot` / `Compose` insets this is a
        shortcut for ``obj + theme``; for image insets the theme is
        stored on the adapter and drives a sibling `Rectangle` via
        `plot_background`.
        """
        from ..ggplot import ggplot
        from ..themes.theme import theme
        from ._compose import Compose

        if not isinstance(other, theme):
            return NotImplemented
        new = deepcopy(self)
        if isinstance(new.obj, (ggplot, Compose, _InsetImage)):
            new.obj = new.obj + other
        return new

    @property
    def _blank_host(self) -> ggplot:
        """
        Implicit host for rendering this inset standalone

        The host is a `ggplot` with no data and a theme override that
        erases the panel background. Figure size, plot margin, fonts,
        etc. come from the user's default theme. A fresh host is built
        per access — no shared state.
        """
        from ..ggplot import ggplot
        from ..themes.elements import element_rect
        from ..themes.theme import theme

        return ggplot() + theme(panel_background=element_rect(fill="none"))

    def draw(self, *, show: bool = False) -> Figure:
        """
        Render this inset standalone on an implicit blank host

        Parameters
        ----------
        show :
            Whether to show the plot.
        """
        return (self._blank_host + self).draw(show=show)

    def show(self):
        """
        Display this inset using the matplotlib backend set by the user
        """
        (self._blank_host + self).show()

    def save(self, *args: Any, **kwargs: Any):
        """
        Save this inset as an image file

        Accepts the same arguments as [](`~plotnine.ggplot.save`).
        """
        (self._blank_host + self).save(*args, **kwargs)

    def _repr_mimebundle_(self, include=None, exclude=None):
        return (self._blank_host + self)._repr_mimebundle_(
            include=include, exclude=exclude
        )

    def __repr__(self):
        from .._utils.quarto import is_knitr_engine

        if is_knitr_engine():
            self.show()
            return ""
        return super().__repr__()

    def _draw_in_host(self):
        """
        Render this inset against an already-set-up host figure

        For standalone use, call `draw()` instead.
        """
        from ..ggplot import ggplot
        from ._compose import Compose

        if isinstance(self.obj, (ggplot, Compose, _InsetImage)):
            self.obj.draw()

    def __radd__(self, other: ggplot) -> ggplot:
        """
        Attach this inset to a ggplot
        """
        other._insets.append(deepcopy(self))
        return other


class Insets(list[inset_element]):
    """
    List of insets attached to a ggplot
    """

    def _setup(self, parent: ggplot):
        """
        Inherit the host figure and figure-owner-only theme props
        """
        for inset in self:
            inset._setup(parent)

    def draw(self, which: Literal["above", "below"]):
        """
        Render insets in a single band, in paint order

        Parameters
        ----------
        which :
            ``"above"`` paints above-insets only, in declaration
            order. ``"below"`` paints below-insets only,
            last-declared first so it lands closest to the host.
        """
        if which == "above":
            insets = [inset for inset in self if inset.on_top]
        else:
            insets = [inset for inset in self if not inset.on_top][::-1]

        for inset in insets:
            inset._draw_in_host()

    def __and__(self, rhs) -> Insets:
        """
        Apply rhs to every inset's obj, recursing into nested structure

        Insets that themselves have insets receive `obj & rhs` so the
        broadcast reaches every nested child.
        """
        from ..ggplot import ggplot
        from ._compose import Compose

        new = Insets(deepcopy(self))
        for inset in new:
            if isinstance(inset.obj, Compose) or (
                isinstance(inset.obj, ggplot) and inset.obj._insets
            ):
                inset.obj = inset.obj & rhs
            else:
                inset.obj = inset.obj + rhs
        return new

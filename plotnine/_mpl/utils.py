from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

from matplotlib.transforms import Affine2D, Bbox

from plotnine._utils import ha_as_float, va_as_float

from .transforms import ZEROS_BBOX

if TYPE_CHECKING:
    from typing import Literal, Sequence

    from matplotlib.artist import Artist
    from matplotlib.axes import Axes
    from matplotlib.backend_bases import RendererBase
    from matplotlib.figure import Figure
    from matplotlib.gridspec import SubplotSpec
    from matplotlib.text import Text
    from matplotlib.transforms import Transform

    from plotnine.typing import HorizontalJustification, VerticalJustification

    from .gridspec import p9GridSpec


def bbox_in_figure_space(
    artist: Artist, fig: Figure, renderer: RendererBase
) -> Bbox:
    """
    Bounding box of artist in figure coordinates
    """
    box = artist.get_window_extent(renderer) or ZEROS_BBOX
    return fig.transFigure.inverted().transform_bbox(box)


def tight_bbox_in_figure_space(
    artist: Artist, fig: Figure, renderer: RendererBase
) -> Bbox:
    """
    Bounding box of artist and its children in figure coordinates
    """
    box = artist.get_tightbbox(renderer) or ZEROS_BBOX
    return fig.transFigure.inverted().transform_bbox(box)


def bbox_in_axes_space(
    artist: Artist, ax: Axes, renderer: RendererBase
) -> Bbox:
    """
    Bounding box of artist in figure coordinates
    """
    box = artist.get_window_extent(renderer) or ZEROS_BBOX
    return ax.transAxes.inverted().transform_bbox(box)


def pts_in_figure_space(fig: Figure, pts: float) -> float:
    """
    Points in figure coordinates
    """
    return fig.transFigure.inverted().transform([0, pts])[1]


def get_transPanels(fig: Figure, gs: p9GridSpec) -> Transform:
    """
    Coordinate system of the Panels (facets) area

    (0, 0) is the bottom-left of the bottom-left panel and
    (1, 1) is the top right of the top-right panel.

    The gridspec parameters must be set before calling this function.
    i.e. gs.update have been called.
    """
    # The position of the panels area in figure coordinates
    params = gs.get_subplot_params(fig)

    # Figure width & height in display coordinates
    W, H = fig.bbox.width, fig.bbox.height

    # 1. The panels occupy space that is smaller than the figure
    # 2. That space is contained within the figure
    # We create a transform that represents these separable aspects
    # (but order matters), and use it to transform transFigure
    sx, sy = params.right - params.left, params.top - params.bottom
    dx, dy = params.left * W, params.bottom * H
    transFiguretoPanels = Affine2D().scale(sx, sy).translate(dx, dy)
    return fig.transFigure + transFiguretoPanels


def rel_position(rel: float, length: float, low: float, high: float) -> float:
    """
    Relatively position an object of a given length between two position

    Parameters
    ----------
    rel:
        Relative position of the object between the limits.
    length:
        Length of the object
    low:
        Lower limit position
    high:
        Upper limit position
    """
    return low * (1 - rel) + (high - length) * rel


def get_subplotspecs(axs: list[Axes]) -> list[SubplotSpec]:
    """
    Return the SubplotSpecs of the given axes

    Parameters
    ----------
    axs:
        List of axes

    Notes
    -----
    This functions returns the innermost subplotspec and it expects
    every axes object to have one.
    """
    subplotspecs: list[SubplotSpec] = []
    for ax in axs:
        if not (subplotspec := ax.get_subplotspec()):
            raise ValueError("Axes has no suplotspec")
        subplotspecs.append(subplotspec)
    return subplotspecs


def draw_gridspec(gs: p9GridSpec, color="black", **kwargs):
    """
    A debug function to draw a rectangle around the gridspec
    """
    draw_bbox(gs.bbox_relative, gs.figure, color, **kwargs)


def draw_bbox(bbox, figure, color="black", **kwargs):
    """
    A debug function to draw a rectangle around a bounding bbox
    """
    from matplotlib.patches import Rectangle

    figure.add_artist(
        Rectangle(
            xy=bbox.p0,
            width=bbox.width,
            height=bbox.height,
            edgecolor=color,
            fill="facecolor" in kwargs,
            clip_on=False,
            **kwargs,
        )
    )


@dataclass
class ArtistGeometry:
    """
    Helper to calculate the position & extents (space) of an artist
    """

    figure: Figure

    def __post_init__(self):
        self.renderer = cast("RendererBase", self.figure._get_renderer())  # pyright: ignore

    def bbox(self, artist: Artist) -> Bbox:
        """
        Bounding box of artist in figure coordinates
        """
        return bbox_in_figure_space(artist, self.figure, self.renderer)

    def tight_bbox(self, artist: Artist) -> Bbox:
        """
        Bounding box of artist and its children in figure coordinates
        """
        return tight_bbox_in_figure_space(artist, self.figure, self.renderer)

    def width(self, artist: Artist) -> float:
        """
        Width of artist in figure space
        """
        return self.bbox(artist).width

    def tight_width(self, artist: Artist) -> float:
        """
        Width of artist and its children in figure space
        """
        return self.tight_bbox(artist).width

    def height(self, artist: Artist) -> float:
        """
        Height of artist in figure space
        """
        return self.bbox(artist).height

    def tight_height(self, artist: Artist) -> float:
        """
        Height of artist and its children in figure space
        """
        return self.tight_bbox(artist).height

    def size(self, artist: Artist) -> tuple[float, float]:
        """
        (width, height) of artist in figure space
        """
        bbox = self.bbox(artist)
        return (bbox.width, bbox.height)

    def tight_size(self, artist: Artist) -> tuple[float, float]:
        """
        (width, height) of artist and its children in figure space
        """
        bbox = self.tight_bbox(artist)
        return (bbox.width, bbox.height)

    def left_x(self, artist: Artist) -> float:
        """
        x value of the left edge of the artist

         ---
        x   |
         ---
        """
        return self.bbox(artist).min[0]

    def right_x(self, artist: Artist) -> float:
        """
        x value of the left edge of the artist

         ---
        |   x
         ---
        """
        return self.bbox(artist).max[0]

    def top_y(self, artist: Artist) -> float:
        """
        y value of the top edge of the artist

         -y-
        |   |
         ---
        """
        return self.bbox(artist).max[1]

    def bottom_y(self, artist: Artist) -> float:
        """
        y value of the bottom edge of the artist

         ---
        |   |
         -y-
        """
        return self.bbox(artist).min[1]

    def max_width(self, artists: Sequence[Artist]) -> float:
        """
        Return the maximum width of list of artists
        """
        widths = [
            bbox_in_figure_space(a, self.figure, self.renderer).width
            for a in artists
        ]
        return max(widths) if len(widths) else 0

    def max_height(self, artists: Sequence[Artist]) -> float:
        """
        Return the maximum height of list of artists
        """
        heights = [
            bbox_in_figure_space(a, self.figure, self.renderer).height
            for a in artists
        ]
        return max(heights) if len(heights) else 0


@dataclass
class JustifyBoundaries:
    """
    Limits about which text can be justified
    """

    plot_left: float
    plot_right: float
    plot_bottom: float
    plot_top: float
    panel_left: float
    panel_right: float
    panel_bottom: float
    panel_top: float


class TextJustifier:
    """
    Justify Text

    The justification methods reinterpret alignment values to be justification
    about a span.
    """

    def __init__(self, figure: Figure, boundaries: JustifyBoundaries):
        self.geometry = ArtistGeometry(figure)
        self.boundaries = boundaries

    def horizontally(
        self,
        text: Text,
        ha: HorizontalJustification | float,
        left: float,
        right: float,
        width: float | None = None,
    ):
        """
        Horizontally Justify text between left and right
        """
        rel = ha_as_float(ha)
        if width is None:
            width = self.geometry.width(text)
        x = rel_position(rel, width, left, right)
        text.set_x(x)
        text.set_horizontalalignment("left")

    def vertically(
        self,
        text: Text,
        va: VerticalJustification | float,
        bottom: float,
        top: float,
        height: float | None = None,
    ):
        """
        Vertically Justify text between bottom and top
        """
        rel = va_as_float(va)

        if height is None:
            height = self.geometry.height(text)
        y = rel_position(rel, height, bottom, top)
        text.set_y(y)
        text.set_verticalalignment("bottom")

    def horizontally_across_panel(
        self, text: Text, ha: HorizontalJustification | float
    ):
        """
        Horizontally Justify text accross the panel(s) width
        """
        self.horizontally(
            text, ha, self.boundaries.panel_left, self.boundaries.panel_right
        )

    def horizontally_across_plot(
        self, text: Text, ha: HorizontalJustification | float
    ):
        """
        Horizontally Justify text across the plot's width
        """
        self.horizontally(
            text, ha, self.boundaries.plot_left, self.boundaries.plot_right
        )

    def vertically_along_panel(
        self, text: Text, va: VerticalJustification | float
    ):
        """
        Horizontally Justify text along the panel(s) height
        """
        self.vertically(
            text, va, self.boundaries.panel_bottom, self.boundaries.panel_top
        )

    def vertically_along_plot(
        self, text: Text, va: VerticalJustification | float
    ):
        """
        Vertically Justify text along the plot's height
        """
        self.vertically(
            text, va, self.boundaries.plot_bottom, self.boundaries.plot_top
        )

    def horizontally_about(
        self, text: Text, ratio: float, how: Literal["panel", "plot"]
    ):
        """
        Horizontally Justify text across the panel or plot
        """
        if how == "panel":
            self.horizontally_across_panel(text, ratio)
        else:
            self.horizontally_across_plot(text, ratio)

    def vertically_about(
        self, text: Text, ratio: float, how: Literal["panel", "plot"]
    ):
        """
        Vertically Justify text along the panel or plot
        """
        if how == "panel":
            self.vertically_along_panel(text, ratio)
        else:
            self.vertically_along_plot(text, ratio)

from __future__ import annotations

from typing import TYPE_CHECKING

from matplotlib.transforms import Affine2D, Bbox

from .transforms import ZEROS_BBOX

if TYPE_CHECKING:
    from matplotlib.artist import Artist
    from matplotlib.axes import Axes
    from matplotlib.backend_bases import RendererBase
    from matplotlib.figure import Figure
    from matplotlib.gridspec import SubplotSpec
    from matplotlib.transforms import Transform

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

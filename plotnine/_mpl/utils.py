from __future__ import annotations

import typing

from matplotlib.transforms import Affine2D, Bbox

from .transforms import ZEROS_BBOX

if typing.TYPE_CHECKING:
    from matplotlib.artist import Artist
    from matplotlib.axes import Axes
    from matplotlib.backend_bases import RendererBase
    from matplotlib.figure import Figure
    from matplotlib.transforms import Transform


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


def get_transPanels(fig: Figure) -> Transform:
    """
    Coordinate system of the Panels (facets) area

    (0, 0) is the bottom-left of the bottom-left panel and
    (1, 1) is the top right of the top-right panel.

    The subplot parameters must be set before calling this function.
    i.e. fig.subplots_adjust should have been called.
    """
    # Contains the layout information from which the panel area
    # is derived
    params = fig.subplotpars

    # Figure width & height in display coordinates
    W, H = fig.bbox.width, fig.bbox.height

    # 1. The panels occupy space that is smaller than the figure
    # 2. That space is contained within the figure
    # We create a transform that represent these separable aspects
    # (but order matters), and use to transform transFigure
    sx, sy = params.right - params.left, params.top - params.bottom
    dx, dy = params.left * W, params.bottom * H
    transFiguretoPanels = Affine2D().scale(sx, sy).translate(dx, dy)
    return fig.transFigure + transFiguretoPanels

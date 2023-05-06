from __future__ import annotations

import typing

from .transforms import ZEROS_BBOX

if typing.TYPE_CHECKING:
    from matplotlib.backend_bases import RendererBase
    from matplotlib.transforms import Bbox

    from plotnine.typing import (
        Artist,
        Axes,
        Figure,
    )


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
    Bounding box of artist in figure coordinates
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

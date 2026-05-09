from __future__ import annotations

import typing
from warnings import warn

from .exceptions import PlotnineWarning

if typing.TYPE_CHECKING:
    import pathlib
    from typing import Any, Optional

    import matplotlib.figure

    import plotnine as p9

__all__ = ("watermark",)


class watermark:
    """
    Add watermark to plot

    Parameters
    ----------
    filename :
        Image file
    xo :
        x position offset in pixels.
    yo :
        y position offset in pixels.
    alpha :
        Alpha blending value.
    kwargs :
        Additional parameters passed to
        [](`~matplotlib.figure.figimage`). Note that ``zorder`` is
        managed by plotnine and any user-supplied value is dropped.

    Notes
    -----
    You can add more than one watermark to a plot.
    """

    _parent: p9.ggplot

    def __init__(
        self,
        filename: str | pathlib.Path,
        xo: int = 0,
        yo: int = 0,
        alpha: Optional[float] = None,
        **kwargs: Any,
    ):
        self.filename = filename
        if "zorder" in kwargs:
            warn(
                "watermark zorder is managed by plotnine; "
                "the user-supplied value is being ignored.",
                PlotnineWarning,
                stacklevel=2,
            )
            kwargs.pop("zorder")
        kwargs.update(xo=xo, yo=yo, alpha=alpha)
        self.kwargs = kwargs

    def __radd__(self, other: p9.ggplot) -> p9.ggplot:
        """
        Add watermark to ggplot object
        """
        self._parent = other
        other.watermarks.append(self)
        return other

    def draw(self, figure: matplotlib.figure.Figure):
        """
        Draw watermark

        Parameters
        ----------
        figure :
            Matplolib figure on which to draw
        """
        from matplotlib.image import imread

        figure.figimage(imread(self.filename), **self.kwargs)

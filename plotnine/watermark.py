from __future__ import annotations

import typing

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
        [](`~matplotlib.figure.figimage`)

    Notes
    -----
    You can add more than one watermark to a plot.
    """

    def __init__(
        self,
        filename: str | pathlib.Path,
        xo: int = 0,
        yo: int = 0,
        alpha: Optional[float] = None,
        **kwargs: Any,
    ):
        self.filename = filename
        kwargs.update(xo=xo, yo=yo, alpha=alpha)
        if "zorder" not in kwargs:
            kwargs["zorder"] = 99.9
        self.kwargs = kwargs

    def __radd__(self, other: p9.ggplot) -> p9.ggplot:
        """
        Add watermark to ggplot object
        """
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

        X = imread(self.filename)
        figure.figimage(X, **self.kwargs)

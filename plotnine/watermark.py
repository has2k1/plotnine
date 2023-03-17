from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    import pathlib
    from typing import Any

    import matplotlib.figure

    import plotnine as p9


class watermark:
    """
    Add watermark to plot

    Parameters
    ----------
    filename : str | pathlib.Path
        Image file
    xo : int, optional
        x position offset in pixels. Default is 0.
    yo : int, optional
        y position offset in pixels. Default is 0.
    alpha : float, optional
        Alpha blending value.
    kwargs : dict
        Additional parameters passed to
        :meth:`matplotlib.figure.figimage`.

    Notes
    -----
    You can add more than one watermark to a plot.
    """

    def __init__(
        self,
        filename: str | pathlib.Path,
        xo: int = 0,
        yo: int = 0,
        alpha: float | None = None,
        **kwargs: Any,
    ):
        self.filename = filename
        kwargs.update(xo=xo, yo=yo, alpha=alpha)
        if "zorder" not in kwargs:
            kwargs["zorder"] = 99.9
        self.kwargs = kwargs

    def __radd__(self, gg: p9.ggplot) -> p9.ggplot:
        """
        Add watermark to ggplot object
        """
        gg.watermarks.append(self)
        return gg

    def draw(self, figure: matplotlib.figure.Figure):
        """
        Draw watermark

        Parameters
        ----------
        figure : Matplotlib.figure.Figure
            Matplolib figure on which to draw
        """
        from matplotlib.image import imread

        X = imread(self.filename)
        figure.figimage(X, **self.kwargs)

from __future__ import annotations

import typing

from .._utils import to_rgba
from ..doctools import document
from .geom_text import geom_text

if typing.TYPE_CHECKING:
    from typing import Any

    import pandas as pd
    from matplotlib.offsetbox import DrawingArea

    from plotnine.layer import layer


_aes = geom_text.DEFAULT_AES.copy()
_aes["fill"] = "white"

_params = geom_text.DEFAULT_PARAMS.copy()
_params.update(
    {
        # boxstyle is one of
        #   cirle, larrow, rarrow, round, round4,
        #   roundtooth, sawtooth, square
        #
        # Documentation at matplotlib.patches.BoxStyle
        "boxstyle": "round",
        "boxcolor": None,
        "label_padding": 0.25,
        "label_r": 0.25,
        "label_size": 0.7,
        "tooth_size": None,
    }
)


@document
class geom_label(geom_text):
    """
    Textual annotations with a background

    {usage}

    Parameters
    ----------
    {common_parameters}
    boxstyle : str, default="round"
        Options are:
        ```python
        'circle'
        'darrow'
        'larrow'
        'rarrow'
        'round '
        'round4'
        'roundtooth'
        'sawtooth'
        'square'
        ````
    boxcolor: str, tuple[float, float, float, float], default=None
        Color of box around the text. If None, the color is
        the same as the text.
    label_padding : float, default=0.25
        Amount of padding
    label_r : float, default=0.25
        Rounding radius of corners.
    label_size : float, default=0.7
        Linewidth of the label boundary.
    tooth_size : float, default=None
        Size of the `roundtooth` or `sawtooth` if they
        are the chosen *boxstyle*. The default depends
        on Matplotlib

    See Also
    --------
    plotnine.geom_text : For documentation of the
        parameters. [](`~matplotlib.patches.BoxStyle`) for the
        parameters that affect the boxstyle.
    """

    DEFAULT_AES = _aes
    DEFAULT_PARAMS = _params

    @staticmethod
    def draw_legend(
        data: pd.Series[Any], da: DrawingArea, lyr: layer
    ) -> DrawingArea:
        """
        Draw letter 'a' in the box

        Parameters
        ----------
        data : Series
            Data Row
        da : DrawingArea
            Canvas
        lyr : layer
            Layer

        Returns
        -------
        out : DrawingArea
        """
        from matplotlib.patches import Rectangle

        fill = to_rgba(data["fill"], data["alpha"])

        if data["fill"]:
            rect = Rectangle(
                (0, 0),
                width=da.width,
                height=da.height,
                linewidth=0,
                facecolor=fill,
                capstyle="projecting",
            )
            da.add_artist(rect)
        return geom_text.draw_legend(data, da, lyr)

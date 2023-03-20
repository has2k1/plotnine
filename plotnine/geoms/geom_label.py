from __future__ import annotations

import typing

from ..doctools import document
from ..utils import to_rgba
from .geom_text import geom_text

if typing.TYPE_CHECKING:
    from typing import Any

    import pandas as pd

    from plotnine.typing import DrawingArea, Layer


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
    boxstyle : str, optional (default: round)
        Options are::

            'circle'
            'darrow'
            'larrow'
            'rarrow'
            'round '
            'round4'
            'roundtooth'
            'sawtooth'
            'square'
    boxcolor: None, str or rgba tuple (default: None)
        Color of box around the text. If None, the color is
        the same as the text.
    label_padding : float, optional (default: 0.25)
        Amount of padding
    label_r : float, optional (default: 0.25)
        Rounding radius of corners.
    label_size : float, optional (default: 0.7)
        Linewidth of the label boundary.
    tooth_size : float, optional (default: None)
        Size of the ``roundtooth`` or ``sawtooth`` if they
        are the chosen *boxstyle*. The default depends
        on Matplotlib

    See Also
    --------
    plotnine.geoms.geom_text : For documentation of the
        parameters. :class:`matplotlib.patches.BoxStyle` for the
        parameters that affect the boxstyle.
    """

    DEFAULT_AES = _aes
    DEFAULT_PARAMS = _params

    @staticmethod
    def draw_legend(
        data: pd.Series[Any], da: DrawingArea, lyr: Layer
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

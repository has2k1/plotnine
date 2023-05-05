from __future__ import annotations

import typing

from .exceptions import PlotnineError
from .iapi import labels_view
from .mapping.aes import SCALED_AESTHETICS, rename_aesthetics

if typing.TYPE_CHECKING:
    import plotnine as p9

__all__ = ["xlab", "ylab", "labs", "ggtitle"]
VALID_LABELS = SCALED_AESTHETICS | {"caption", "title", "subtitle"}


class labs:
    """
    Add labels for aesthetics and/or title

    Parameters
    ----------
    kwargs : dict
        Aesthetics (with scales) to be renamed. You can also
        set the ``title`` and ``caption``.
    """

    labels: labels_view

    def __init__(self, **kwargs: str):
        unknown = kwargs.keys() - VALID_LABELS
        if unknown:
            raise PlotnineError(f"Cannot deal with these labels: {unknown}")
        self.labels = labels_view(**rename_aesthetics(kwargs))

    def __radd__(self, gg: p9.ggplot) -> p9.ggplot:
        """
        Add labels to ggplot object
        """
        gg.labels.update(self.labels)
        return gg


class xlab(labs):
    """
    Create x-axis label

    Parameters
    ----------
    xlab : str
        x-axis label
    """

    def __init__(self, xlab: str):
        if xlab is None:
            raise PlotnineError("Arguments to xlab cannot be None")
        self.labels = labels_view(x=xlab)


class ylab(labs):
    """
    Create y-axis label

    Parameters
    ----------
    ylab : str
        y-axis label
    """

    def __init__(self, ylab: str):
        if ylab is None:
            raise PlotnineError("Arguments to ylab cannot be None")
        self.labels = labels_view(y=ylab)


class ggtitle(labs):
    """
    Create plot title

    Parameters
    ----------
    title : str
        Plot title
    """

    def __init__(self, title: str):
        if title is None:
            raise PlotnineError("Arguments to ggtitle cannot be None")
        self.labels = labels_view(title=title)

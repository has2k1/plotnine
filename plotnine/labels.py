from __future__ import annotations
from copy import deepcopy

from .mapping.aes import rename_aesthetics, SCALED_AESTHETICS
from .exceptions import PlotnineError

import typing
if typing.TYPE_CHECKING:
    import plotnine as p9

__all__ = ['xlab', 'ylab', 'labs', 'ggtitle']
VALID_LABELS = SCALED_AESTHETICS | {'caption', 'title'}


class labs:
    """
    Add labels for aesthetics and/or title

    Parameters
    ----------
    kwargs : dict
        Aesthetics (with scales) to be renamed. You can also
        set the ``title`` and ``caption``.
    """
    labels: dict[str, str] = {}

    def __init__(self, **kwargs: str) -> None:
        unknown = kwargs.keys() - VALID_LABELS
        if unknown:
            raise PlotnineError(
                f"Cannot deal with these labels: {unknown}"
            )
        self.labels = rename_aesthetics(kwargs)

    def __radd__(self, gg: p9.ggplot, inplace: bool = False) -> p9.ggplot:
        """
        Add labels to ggplot object
        """
        gg = gg if inplace else deepcopy(gg)
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

    def __init__(self, xlab: str) -> None:
        if xlab is None:
            raise PlotnineError(
                "Arguments to xlab cannot be None")
        self.labels = {'x': xlab}


class ylab(labs):
    """
    Create y-axis label

    Parameters
    ----------
    ylab : str
        y-axis label
    """

    def __init__(self, ylab: str) -> None:
        if ylab is None:
            raise PlotnineError(
                "Arguments to ylab cannot be None")
        self.labels = {'y': ylab}


class ggtitle(labs):
    """
    Create plot title

    Parameters
    ----------
    title : str
        Plot title
    """

    def __init__(self, title: str) -> None:
        if title is None:
            raise PlotnineError(
                "Arguments to ggtitle cannot be None")
        self.labels = {'title': title}

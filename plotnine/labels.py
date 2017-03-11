from __future__ import absolute_import, division, print_function
from copy import deepcopy

from .exceptions import PlotnineError

__all__ = ['xlab', 'ylab', 'labs', 'ggtitle']


class labs(object):
    """
    General class for all label adding classes

    Parameters
    ----------
    args : dict
        Aesthetics to be renamed
    kwargs : dict
        Aesthetics to be renamed
    """
    labels = {}

    def __init__(self, *args, **kwargs):
        if args and not isinstance(args, dict):
            raise PlotnineError(
                "'labs' accepts either a dictionary as "
                "an argument or keyword arguments")
            self.labels = args
        else:
            self.labels = kwargs

    def __radd__(self, gg, inplace=False):
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

    def __init__(self, xlab):
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

    def __init__(self, ylab):
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
    def __init__(self, title):
        if title is None:
            raise PlotnineError(
                "Arguments to ggtitle cannot be None")
        self.labels = {'title': title}

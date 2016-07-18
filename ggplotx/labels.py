from __future__ import absolute_import, division, print_function
from copy import deepcopy

from .utils.exceptions import GgplotError

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
            raise GgplotError(
                "'labs' accepts either a dictionary as",
                "an argument or keyword arguments")
            self.labels = args
        else:
            self.labels = kwargs

    def __radd__(self, gg):
        gg = deepcopy(gg)
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
            raise GgplotError("Arguments to",
                              self.__class__.__name__,
                              "cannot be None")
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
            raise GgplotError("Arguments to",
                              self.__class__.__name__,
                              "cannot be None")
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
            raise GgplotError("Arguments to",
                              self.__class__.__name__,
                              "cannot be None")
        self.labels = {'title': title}

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from copy import deepcopy
from ..utils.exceptions import GgplotError


class labs(object):
    """
    General class for all label adding classes
    """
    labels = {}

    def __init__(self, *args, **kwargs):
        if args and not isinstance(args, dict):
            raise GgplotError(
                "'labs' excepts either a dictionary as",
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
    """
    def __init__(self, title):
        if title is None:
            raise GgplotError("Arguments to",
                              self.__class__.__name__,
                              "cannot be None")
        self.label = {'title': title}

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from copy import deepcopy
from ggplot.utils.exceptions import GgplotError


class ggtitle(object):
    def __init__(self, title):
        if title is None:
            raise GgplotError("Arguments to", self.__class__.__name__,
                              "cannot be None")
        self.title = title

    def __radd__(self, gg):
        gg = deepcopy(gg)
        gg.title = self.title
        return gg


class xlim(object):
    def __init__(self, low, high):
        if low is None or high is None:
            raise GgplotError("Arguments to", self.__class__.__name__,
                              "cannot be None")
        try:
            _ = high - low
        except TypeError:
            raise GgplotError("Arguments to", self.__class__.__name__,
                              "must be of a numeric type")
        self.low, self.high = low, high

    def __radd__(self, gg):
        gg = deepcopy(gg)
        gg.xlimits = [self.low, self.high]
        return gg


class ylim(object):
    def __init__(self, low, high):
        if low is None or high is None:
            raise GgplotError("Arguments to", self.__class__.__name__,
                              "cannot be None")
        try:
            _ = high - low
        except TypeError:
            raise GgplotError("Arguments to", self.__class__.__name__,
                              "must be of a numeric type")
        self.low, self.high = low, high

    def __radd__(self, gg):
        gg = deepcopy(gg)
        gg.ylimits = [self.low, self.high]
        return gg


class xlab(object):
    def __init__(self, xlab):
        if xlab is None:
            raise GgplotError("Arguments to", self.__class__.__name__,
                              "cannot be None")
        self.xlab = xlab

    def __radd__(self, gg):
        gg = deepcopy(gg)
        gg.xlab = self.xlab
        return gg


class ylab(object):
    def __init__(self, ylab):
        if ylab is None:
            raise GgplotError("Arguments to", self.__class__.__name__,
                              "cannot be None")
        self.ylab = ylab

    def __radd__(self, gg):
        gg = deepcopy(gg)
        gg.ylab = self.ylab
        return gg


class labs(object):
    def __init__(self, x=None, y=None, title=None):
        self.x = x
        self.y = y
        self.title = title

    def __radd__(self, gg):
        gg = deepcopy(gg)
        if self.x:
            gg.xlab = self.x
        if self.y:
            gg.ylab = self.y
        if self.title:
            gg.title = self.title
        return gg

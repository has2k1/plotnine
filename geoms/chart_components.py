from copy import deepcopy

class ggtitle(object):
    def __init__(self, title):
        self.title = title

    def __radd__(self, gg):
        gg = deepcopy(gg)
        gg.title = self.title
        return gg

class xlab(object):
    def __init__(self, xlab):
        self.xlab = xlab

    def __radd__(self, gg):
        gg = deepcopy(gg)
        gg.xlab = self.xlab
        return gg

class ylab(object):
    def __init__(self, ylab):
        self.ylab = ylab

    def __radd__(self, gg):
        gg = deepcopy(gg)
        gg.ylab = self.ylab
        return gg

class labs(object):
    def __init__(self, xlab=None, ylab=None):
        self.xlab = xlab
        self.ylab = ylab

    def __radd__(self, gg):
        gg = deepcopy(gg)
        if self.xlab:
            gg.xlab = self.xlab
        if self.ylab:
            gg.ylab = self.ylab
        return gg
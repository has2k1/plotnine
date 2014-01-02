from .scale import scale
from copy import deepcopy


class scale_y_log(scale):
    def __init__(self, base=10):
        self.base = base
    def __radd__(self, gg):
        gg = deepcopy(gg)
        gg.scale_y_log = self.base
        return gg


class scale_x_log(scale):
    def __init__(self, base=10):
        self.base = base
    def __radd__(self, gg, base=10):
        gg = deepcopy(gg)
        gg.scale_x_log = self.base
        return gg


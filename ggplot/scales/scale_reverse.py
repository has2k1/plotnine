from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from .scale import scale
from copy import deepcopy


class scale_y_reverse(scale):

    def __radd__(self, gg):
        gg = deepcopy(gg)
        gg.scale_y_reverse = True
        return gg


class scale_x_reverse(scale):
    def __radd__(self, gg):
        gg = deepcopy(gg)
        gg.scale_x_reverse = True
        return gg

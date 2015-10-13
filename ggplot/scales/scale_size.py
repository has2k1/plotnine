from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np

from ..utils import seq
from .scale import scale_discrete, scale_continuous
from .utils import rescale_pal, rescale_max
from .utils import abs_area, area_pal


class scale_size_discrete(scale_discrete):
    aesthetics = ['size']

    def __init__(self, range=(2, 6), **kwargs):
        def palette(n):
            area = seq(range[0]**2, range[1]**2, n)
            return np.sqrt(area)

        self.palette = palette
        scale_discrete.__init__(self, **kwargs)


class scale_size_continuous(scale_continuous):
    aesthetics = ['size']

    def __init__(self, range=(1, 6), **kwargs):
        self.palette = area_pal(range)
        scale_continuous.__init__(self, **kwargs)


scale_size = scale_size_continuous


class scale_size_radius(scale_continuous):
    aesthetics = ['size']

    def __init__(self, range=(1, 6), **kwargs):
        self.palette = rescale_pal(range)
        scale_continuous.__init__(self, **kwargs)


class scale_size_area(scale_continuous):
    aesthetics = ['size']
    rescaler = staticmethod(rescale_max)

    def __init__(self, max_size=6, **kwargs):
        self.palette = abs_area(max_size)
        scale_continuous.__init__(self, **kwargs)

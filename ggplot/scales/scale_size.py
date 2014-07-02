from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np

from .scale_discrete import scale_discrete
from .scale_continuous import scale_continuous
from .utils import rescale_pal


class scale_size(scale_discrete):
    aesthetics = ['size']

    def __init__(self, range=(1, 6)):
        self.range = range

    def palette(self, n):
        return np.linspace(self.range[0], self.range[1], n)


class scale_size_continuous(scale_continuous):
    aesthetics = ['size']

    def __init__(self, range=(1, 6)):
        palette = staticmethod(rescale_pal(range))


scale_size_discrete = scale_size

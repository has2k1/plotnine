from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np

from .utils import rescale_pal
from .scale import scale_discrete, scale_continuous


class scale_alpha(scale_continuous):
    aesthetics = ['alpha']

    def __init__(self, range=(0.1, 1)):
        self.palette = rescale_pal(range)


class scale_alpha_continuous(scale_alpha):
    pass


class scale_alpha_discrete(scale_discrete):
    aesthetics = ['alpha']

    def __init__(self, range=(0.1, 1)):
        self._alpha_range = range

    def palette(self, n):
        return np.linspace(self._alpha_range[0], self._alpha_range[1], n)

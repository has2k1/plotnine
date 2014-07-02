from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from .utils import rescale_pal
from .scale import scale_discrete, scale_continuous


class scale_alpha(scale_continuous):
    aesthetics = ['alpha']

    def __init__(self, range=(0.1, 1)):
        self.palette = staticmethod(rescale_pal(range))


class scale_alpha_continuous(scale_alpha):
    pass


class scale_alpha_discrete(scale_discrete):
    aesthetics = ['alpha']

    def __init__(self, range=(0.1, 1)):
        self.range = range

    def palette(self, n):
        return np.linspace(self.range[0], self.range[1], n)

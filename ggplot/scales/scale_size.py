from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np

from .scale import scale_discrete, scale_continuous
from .utils import rescale_pal


class scale_size_discrete(scale_discrete):
    aesthetics = ['size']

    def __init__(self, range=(1, 6), **kwargs):
        def palette(n):
            return np.linspace(range[0], range[1], n)
        kwargs['palette'] = palette
        scale_discrete.__init__(self, **kwargs)


class scale_size_continuous(scale_continuous):
    aesthetics = ['size']

    def __init__(self, range=(1, 6), **kwargs):
        kwargs['palette'] = rescale_pal(range)
        scale_continuous.__init__(self, **kwargs)


scale_size = scale_size_continuous

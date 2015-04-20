from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np

from .utils import rescale_pal
from .scale import scale_discrete, scale_continuous


class scale_alpha(scale_continuous):
    aesthetics = ['alpha']

    def __init__(self, range=(0.1, 1), **kwargs):
        kwargs['palette'] = rescale_pal(range)
        scale_continuous.__init__(self, **kwargs)


scale_alpha_continuous = scale_alpha


class scale_alpha_discrete(scale_discrete):
    aesthetics = ['alpha']

    def __init__(self, range=(0.1, 1), **kwargs):
        def palette(n):
            return np.linspace(range[0], range[1], n)
        kwargs['palette'] = palette
        scale_discrete.__init__(self, **kwargs)

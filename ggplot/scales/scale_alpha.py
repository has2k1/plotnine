from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
from mizani.palettes import rescale_pal

from ..utils import alias
from .scale import scale_discrete, scale_continuous


class scale_alpha(scale_continuous):
    """
    Continuous Alpha Scale

    Parameters
    ----------
    range : array_like
        Range ([Minimum, Maximum]) of output alpha values.
        Should be between 0 and 1. Default is ``(0.1, 1)``
    kwargs : dict
        Parameters passed on to :class:`.scale_continuous`
    """
    aesthetics = ['alpha']

    def __init__(self, range=(0.1, 1), **kwargs):
        self.palette = rescale_pal(range)
        scale_continuous.__init__(self, **kwargs)


alias('scale_alpha_continuous', scale_alpha)


class scale_alpha_discrete(scale_discrete):
    """
    Discrete Alpha Scale

    Parameters
    ----------
    range : array_like
        Range ([Minimum, Maximum]) of output alpha values.
        Should be between 0 and 1. Default is ``(0.1, 1)``
    kwargs : dict
        Parameters passed on to :class:`.scale_discrete`
    """
    aesthetics = ['alpha']

    def __init__(self, range=(0.1, 1), **kwargs):
        def palette(n):
            return np.linspace(range[0], range[1], n)

        self.palette = palette
        scale_discrete.__init__(self, **kwargs)

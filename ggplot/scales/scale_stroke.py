from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from ..utils.exceptions import GgplotError
from .scale import scale_discrete, scale_continuous
from .utils import rescale_pal


class scale_stroke_continuous(scale_continuous):
    aesthetics = ['stroke']

    def __init__(self, range=(1, 6), **kwargs):
        self.palette = rescale_pal(range)
        scale_continuous.__init__(self, **kwargs)


class scale_stroke_discrete(scale_discrete):
    def __init__(self):
        raise GgplotError(
            "A discrete variable can not be mapped to stroke")


scale_stroke = scale_stroke_continuous

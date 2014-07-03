from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from .scale import scale_discrete, scale_continuous
from ..utils.exceptions import GgplotError


def shape_pal():
    shapes = [
        'o',#circle
        '^',#triangle up
        's',#square
        '+',#plus
        'D',#diamond
        'v',#triangle down
        'x',#x
        '*',#star
        'p',#pentagon
        '8'#octagon
    ]
    def func(n):
        l = list(shapes)
        if n <= len(shapes):
            return l[:n]
        else:
            return l + [None] * (n - len(shapes))
    return func


class scale_shape(scale_discrete):
    aesthetics = ['shape']
    palette = staticmethod(shape_pal())


class scale_shape_continuous(scale_continuous):
    def __init__(self):
        raise GgplotError(
            "A continuous variable can not be mapped to shape")


scale_shape_discrete = scale_shape

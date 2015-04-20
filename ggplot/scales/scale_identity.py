from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from ..utils import identity
from .scale import scale_discrete, scale_continuous


class scale_color_identity(scale_discrete):
    aesthetics = ['color']
    palette = staticmethod(identity)


class scale_fill_identity(scale_color_identity):
    aesthetics = ['fill']


class scale_shape_identity(scale_discrete):
    aesthetics = ['shape']
    palette = staticmethod(identity)


class scale_linetype_identity(scale_discrete):
    aesthetics = ['linetype']
    palette = staticmethod(identity)


class scale_alpha_identity(scale_continuous):
    aesthetics = ['alpha']
    palette = staticmethod(identity)


class scale_size_identity(scale_continuous):
    aesthetics = ['size']
    palette = staticmethod(identity)


# American to British spelling
scale_colour_identity = scale_color_identity

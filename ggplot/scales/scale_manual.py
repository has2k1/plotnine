from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import sys

from .scale import scale_discrete
from ..utils.exceptions import GgplotError

_TPL_SMALL_SCALE = """\
Insufficient values in manual scale. , {}, needed but only , {},  provided.
"""

class _scale_manual(scale_disrete):
    """
    Abstract class for manual scales
    """
    def __init__(self, values):
        self.values

    def palette(self, n):
        if n > len(self.values):
            raise GgplotError(
                _TPL_SMALL_SCALE.format(n, len(self.values)))
        return values


class scale_color_manual(_scale_manual):
    aesthetics = ['color']


class scale_fill_manual(_scale_manual):
    aesthetics = ['fill']


class scale_shape_manual(_scale_manual):
    aesthetics = ['shape']


class scale_linetype_manual(_scale_manual):
    aesthetics = ['linetype']


class scale_alpha_manual(_scale_manual):
    aesthetics = ['alpha']


class scale_size_manual(_scale_manual):
    aesthetics = ['size']


# American to British spelling
scale_colour_manual = scale_color_manual

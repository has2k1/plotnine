from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from ..utils import waiver, identity
from .scale import scale_discrete, scale_continuous


class scale_x_discrete(scale_discrete):
    aethetics = ["x", "xmin", "xmax", "xend"]
    palette = staticmethod(identity)
    guide = None


class scale_y_discrete(scale_discrete):
    aethetics = ["y", "ymin", "ymax", "yend"]
    palette = staticmethod(identity)
    guide = None


class scale_x_continuous(scale_continuous):
    aesthetics = ["x", "xmin", "xmax", "xend", "xintercept"]
    palette = staticmethod(identity)
    guide = None


class scale_y_continuous(scale_continuous):
    aesthetics = ["y", "ymin", "ymax", "yend", "yintercept",
                  "ymin_final", "ymax_final"]
    palette = staticmethod(identity)
    guide = None




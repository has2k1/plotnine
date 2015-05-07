from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from copy import deepcopy

import pandas as pd

from ..scales.scales import make_scale
from ..utils.exceptions import GgplotError


# By adding limits, we create a scale of the appropriate type

class _lim(object):
    aesthetic = None

    def __init__(self, *limits):
        if not limits:
            msg = '{}lim(), is missing limits'
            raise GgplotError(msg.format(self.aesthetic))
        elif len(limits) == 1:
            limits = limits[0]
        s = pd.Series(limits)
        trans = 'reverse' if s[0] > s[1] else 'identity'
        self.scale = make_scale(self.aesthetic, s,
                                limits=limits, trans=trans)

    def __radd__(self, gg):
        gg = deepcopy(gg)
        gg.scales.append(self.scale)
        return gg


class xlim(_lim):
    aesthetic = 'x'


class ylim(_lim):
    aesthetic = 'y'

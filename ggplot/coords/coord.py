from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from copy import deepcopy

from matplotlib.cbook import Bunch

from ..utils import is_waive
from ..utils.exceptions import GgplotError
from ..scales.scale import scale_continuous, scale_discrete


class coord(object):
    """
    Base class for all coordinate systems
    """

    def __radd__(self, gg):
        gg = deepcopy(gg)
        gg.coordinates = self
        return gg

    def expand(self, scale, discrete=(0, 0.6), continuous=(0.05, 0)):
        """
        Expand a single scale
        """
        if is_waive(scale.expand):
            if isinstance(scale, scale_discrete):
                return discrete
            elif isinstance(scale, scale_continuous):
                return continuous
            else:
                name = scale.__class__.__name__
                msg = "Failed to expand scale '{}'".format(name)
                raise GgplotError(msg)
        else:
            return scale.expand

    def range(self, scales):
        """
        Return the range along the dimensions of the coordinate system
        """
        # Defaults to providing the 2D x-y ranges
        return Bunch(x=scales['x_range'], y=scales['y_range'])

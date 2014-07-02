from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from copy import deepcopy

from ..utils import waiver, identity


class scale(object):
    """
    Base class for all scales
    """
    aesthetics = None  # aesthetics affected by this scale
    palette = None     # aesthetic mapping function
    range = None       # range of aesthetic
    limits = None      # (min, max)
    trans = None       # transformation function
    na_value = None    # What to do with the NA values
    expand = waiver()  #
    breaks = waiver()  # major breaks
    labels = waiver()  # labels at the breaks
    guide = waiver()   # legend or any other guide

    def __radd__(self, gg):
        """
        Add this scales to the list of scales for the
        ggplot object
        """
        gg = deepcopy(gg)
        gg.scales.append(self)
        return gg


class scale_discrete(scale):
    """
    Base class for all discrete scales
    """
    pass


class scale_continuous(scale):
    """
    Base class for all continuous scales
    """
    rescaler = None  # Used by diverging and n colour gradients
    oob = None       # what to do with out of bounds data points
    minor_breaks = waiver()
    trans = identity  # transformation function

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from copy import deepcopy
import numpy as np
import pandas.core.common as com

from ..utils import waiver, is_waive
from ..utils import identity, discrete_dtypes, match
from .utils import rescale, censor, expand_range


class scale(object):
    """
    Base class for all scales
    """
    aesthetics = None  # aesthetics affected by this scale
    palette = None     # aesthetic mapping function
    range = None       # range of aesthetic
    trans = None       # transformation function
    na_value = np.NaN  # What to do with the NA values
    _expand = waiver() # multiplicative and additive expansion constants.
    breaks = waiver()  # major breaks
    labels = waiver()  # labels at the breaks
    guide = waiver()   # legend or any other guide
    _limits = None     # (min, max)

    def __radd__(self, gg):
        """
        Add this scales to the list of scales for the
        ggplot object
        """
        gg = deepcopy(gg)
        gg.scales.append(self)
        return gg

    def clone(self):
        return deepcopy(self)

    def reset_range(self):
        self.range = None

    @property
    def limits(self):
        # Fall back to the range if the limits
        # are not set or if any is NaN
        if not self._limits is None:
            if not any(map(np.isnan, self._limits)):
                return self._limits
        return self.range

    @limits.setter
    def limits(self, value):
        self._limits = value

    @property
    def expand(self):
        if is_waive(self._expand):
            # default
            return (0, 0)
        else:
            return self._expand

    @expand.setter
    def expand(self, value):
        self._expand = value


class scale_discrete(scale):
    """
    Base class for all discrete scales
    """
    drop = True        # drop unused factor levels from the scale

    def train(self, series, drop=None):
        """
        Train scale

        Parameters
        ----------
        series: pd.series | np.array
            a column of data to train over
        """
        if drop is None:
            drop = self.drop

        if self.range is None:
            self.range = []

        # new range values
        if com.is_categorical_dtype(series):
            rng = list(series.cat.levels)
            if drop:
                rng = [x for x in rng if x in set(series)]
        else:
            rng = list(series.drop_duplicates().sort())

        # update range
        self.range += [x for x in rng if not (x in set(self.range))]

    def dimension(self, expand=None):
        """
        The phyical size of the scale, if a position scale
        Unlike limits, this always returns a numeric vector of length 2
        """
        if expand is None:
            expand = self.expand
        return expand_range(len(self.limits), expand[0], expand[1])


class scale_continuous(scale):
    """
    Base class for all continuous scales
    """
    rescaler = staticmethod(rescale) # Used by diverging & n colour gradients
    oob = staticmethod(censor)  # what to do with out of bounds data points
    minor_breaks = waiver()
    trans = staticmethod(identity)  # transformation function

    def train(self, series):
        """
        Train scale

        Parameters
        ----------
        series: pd.series | np.array
            a column of data to train over
        """
        if not len(series):
            return
        mn = series.min()
        mx = series.max()
        if self.range:
            _mn, _mx = self.range
            mn = np.min([mn, _mn])
            mx = np.max([mx, _mx])
        self.range = [mn, mx]

    def dimension(self, expand=None):
        """
        The phyical size of the scale, if a position scale
        Unlike limits, this always returns a numeric vector of length 2
        """
        if expand is None:
            expand = self.expand
        return expand_range(self.limits, expand[0], expand[1])

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from copy import deepcopy
import numpy as np
import pandas.core.common as com

from ..utils import waiver, identity, discrete_dtypes, match
from .utils import rescale, censor


class scale(object):
    """
    Base class for all scales
    """
    aesthetics = None  # aesthetics affected by this scale
    palette = None     # aesthetic mapping function
    range = None       # range of aesthetic
    trans = None       # transformation function
    na_value = np.NaN  # What to do with the NA values
    expand = waiver()  #
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

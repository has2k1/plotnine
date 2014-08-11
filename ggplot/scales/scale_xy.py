from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import numpy as np

from ..utils import identity, match
from ..utils import discrete_dtypes, continuous_dtypes
from ..utils.exceptions import GgplotError
from .scale import scale_discrete, scale_continuous


# positions scales have a couple of differences (quirks) that
# make necessary to override some of the scale_discrete and
# scale_continuous methods
#
# scale_position_discrete and scale_position_continuous
# are intermediate base classes where the required overiding
# is done


class scale_position_discrete(scale_discrete):
    """
    Base class for discrete position scales
    """
    # Keeps two ranges, range and range_c
    range_c = None

    def reset(self):
        # Can't reset discrete scale because
        # no way to recover values
        self.range_c = None

    def train(self, series):
        # The discrete position scale is capable of doing
        # training for continuous data.
        # This complicates training and mapping, but makes it
        # possible to place objects at non-integer positions,
        # as is necessary for jittering etc.
        if series.dtype in continuous_dtypes:
            # trick the training method into training
            # range_c by temporarily renaming it to range
            backup, self.range = self.range, self.range_c
            self.train_continuous(series)
            # restore
            self.range_c, self.range = self.range, backup
        else:
            # super() does not work well with reloads
            scale_discrete.train(self, series)

    def map(self, series, limits=None):
        # Discrete values are converted into integers starting
        # at 1
        if not limits:
            limits = self.limits
        if series.dtype in discrete_dtypes:
            seq = np.arange(1, len(limits)+1)
            return seq[match(series, limits)]
        return series

    @property
    def limits(self):
        if self._limits:
            return self._limits
        elif self.range:
            # discrete range
            return self.range
        elif self.range_c:
            # discrete limits for a continuous range
            mn = int(np.floor(np.min(self.range_c)))
            mx = int(np.ceil(np.max(self.range_c)))
            return range(mn, mx+1)
        else:
            GgplotError(
                'Lost, do not know what the limits are.')


# Discrete position scales should be able to make use of the train
# method bound to continuous scales
scale_position_discrete.train_continuous = scale_continuous.__dict__['train']


class scale_position_continuous(scale_continuous):
    """
    Base class for continuous position scales
    """

    def map(self, series, limits=None):
        # Position aesthetics don't map, because the coordinate
        # system takes care of it.
        # But the continuous scale has to deal with out of bound points
        if not len(series):
            return series
        if not limits:
            limits = self.limits
        scaled = self.oob(series, limits)
        scaled[np.isnan(scaled)] = self.na_value
        return scaled


class scale_x_discrete(scale_position_discrete):
    aesthetics = ["x", "xmin", "xmax", "xend"]
    palette = staticmethod(identity)
    guide = None


class scale_y_discrete(scale_position_discrete):
    aesthetics = ["y", "ymin", "ymax", "yend"]
    palette = staticmethod(identity)
    guide = None


class scale_x_continuous(scale_position_continuous):
    aesthetics = ["x", "xmin", "xmax", "xend", "xintercept"]
    palette = staticmethod(identity)
    guide = None


class scale_y_continuous(scale_position_continuous):
    aesthetics = ["y", "ymin", "ymax", "yend", "yintercept",
                  "ymin_final", "ymax_final"]
    palette = staticmethod(identity)
    guide = None

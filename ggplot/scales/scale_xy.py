from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from ..utils import waiver, identity
from ..utils import continuous_dtypes
from .scale import scale_discrete, scale_continuous


class scale_x_discrete(scale_discrete):
    aethetics = ["x", "xmin", "xmax", "xend"]
    palette = staticmethod(identity)
    guide = None

    def train(self, series):
        # The discrete position scale is capable of doing
        # trainning for continuous data.
        # This complicates training and mapping, but makes it
        # possible to place objects at non-integer positions,
        # as is necessary for jittering etc.
        if series.dtype in continuous_dtypes:
            self.train_continuous(series)
        else:
            super(scale_y_continuous, self).train(series)


class scale_y_discrete(scale_discrete):
    aethetics = ["y", "ymin", "ymax", "yend"]
    palette = staticmethod(identity)
    guide = None

    def train(self, series):
        if series.dtype in continuous_columns:
            self.train_continuous(series)
        else:
            super(scale_y_continuous, self).train(series)


# Discrete position scales should be able to make use of the train
# method bound to continuous scales
scale_x_discrete.train_continuous = scale_continuous.__dict__['train']
scale_y_discrete.train_continuous = scale_continuous.__dict__['train']


class scale_x_continuous(scale_continuous):
    aesthetics = ["x", "xmin", "xmax", "xend", "xintercept"]
    palette = staticmethod(identity)
    guide = None


class scale_y_continuous(scale_continuous):
    aesthetics = ["y", "ymin", "ymax", "yend", "yintercept",
                  "ymin_final", "ymax_final"]
    palette = staticmethod(identity)
    guide = None

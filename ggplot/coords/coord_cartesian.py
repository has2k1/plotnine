from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from matplotlib.cbook import Bunch

from ..scales.utils import expand_range
from .coord import coord


class coord_cartesian(coord):

    def __init__(self, xlim=None, ylim=None, expand=True):
        self.limits = Bunch(xlim=xlim, ylim=ylim)
        self.expand = expand

    def train(self, scale):
        """
        Train a single coordinate axis
        """
        # Which axis are we dealing with
        name = scale.aesthetics[0]

        # If the coordinate axis has limits of
        # its own we use those for the final range
        if name == 'x':
            limits = self.limits.xlim
        else:
            limits = self.limits.ylim

        if limits is None:
            rangee = scale.dimension()
        else:
            rangee = scale.transform(limits)

        if self.expand:
            expand = self.expand_default(scale)
            rangee = expand_range(rangee, expand[0], expand[1])

        out = scale.break_info(rangee)
        # This is where
        # x_major, x_labels, x_minor, ...
        # range keys are created
        for key in list(out.keys()):
            new_key = '{}_{}'.format(name, key)
            out[new_key] = out.pop(key)
        return out

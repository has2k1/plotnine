from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from matplotlib.cbook import Bunch

from .coord import coord


class coord_cartesian(coord):

    def __init__(self, xlim=None, ylim=None):
        self.limits = Bunch(xlim=xlim, ylim=ylim)

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
            expand = self.expand(scale)
            rangee = scale.dimension(expand)
        else:
            rangee = scale.transform(limits)

        out = scale.break_info(rangee)
        for key in out.keys():
            new_key = '{}_{}'.format(name, key)
            out[new_key] = out.pop(key)
        return out

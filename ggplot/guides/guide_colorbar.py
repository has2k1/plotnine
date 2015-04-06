from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import hashlib

import pandas as pd
from matplotlib.ticker import MaxNLocator

from ..utils.exceptions import gg_warning
from ..scales.scale import scale_continuous
from .guide import guide


class guide_colorbar(guide):
    # bar
    barwidth = None
    barheight = None
    nbin = 20
    raster = True

    # ticks
    ticks = True
    draw_ulim = True
    draw_llim = True

    # parameter
    available_aes = {'colour', 'color', 'fill'}

    def train(self, scale):
        # Do nothing if scales are inappropriate
        if set(scale.aesthetics) & {'color', 'colour', 'fill'} == 0:
            gg_warning('colorbar guide needs color or fill scales.')
            return None

        if not issubclass(scale.__class__, scale_continuous):
            gg_warning('colorbar guide needs continuous scales')
            return None

        # value = breaks (numeric) is used for determining the
        # position of ticks
        breaks = scale.scale_breaks()
        self.key = pd.DataFrame({
            scale.aesthetics[0]: scale.map(breaks),
            'label': scale.scale_labels(),
            'value': breaks})

        bar = MaxNLocator(self.nbin).tick_values(*scale.limits)
        # discard locations in bar not in scale.limits
        bar = filter(lambda x: scale.limits[0] <= x <= scale.limits[1], bar)
        self.bar = pd.DataFrame({
            'color': scale.map(bar),
            'value': bar})

        labels = ' '.join(str(x) for x in self.key['label'])
        info = '\n'.join([self.title, labels,
                          ' '.join(self.bar['color'].tolist()),
                          self.__class__.__name__])
        self.hash = hashlib.md5(info).hexdigest()

    def merge(self, other):
        """
        Simply discards the other guide
        """
        return self

    def create_geoms(self, plot):
        """
        This guide is not geom based
        """
        self.glayers = []
        return self


guide_colourbar = guide_colorbar

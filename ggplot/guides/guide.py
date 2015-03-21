from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import hashlib

import numpy as np
import pandas as pd

from ..scales.scale import scale_continuous
from ..utils import waiver


class guide(object):
    # title
    title = waiver()
    title_position = None
    title_theme = None
    title_hjust = None
    title_vjust = None

    # label
    label = True
    label_position = None
    label_theme = None
    label_hjust = None
    label_vjust = None

    # key
    keywidth = None
    keyheight = None

    # general
    direction = None
    default_unit = 'line'
    override_aes = {}
    reverse = False
    order = 0

    def train(self, scale):
        breaks = scale.scale_breaks()
        key = pd.DataFrame({
            scale.aesthetics[0]: scale.map(breaks),
            'label': scale.scale_labels()})

        # Drop out-of-range values for continuous scale
        # (should use scale$oob?)

        # Currently, numpy does not deal with NA (Not available)
        # When they are introduced, the block below should be
        # adjusted likewise, see ggplot2, guide-lengend.r
        if isinstance(scale, scale_continuous):
            limits = scale.limits
            b = np.asarray(breaks)
            noob = np.logical_and(limits[0] <= b,
                                  b <= limits[1])
            key = key[noob]

        if len(key) == 0:
            return None

        self.key = key

        # create a hash of the important information in the guide
        labels = ' '.join(str(x) for x in self.key['label'])
        info = '\n'.join([self.title, labels, str(self.direction),
                          self.__class__.__name__])
        self.hash = hashlib.md5(info).hexdigest()

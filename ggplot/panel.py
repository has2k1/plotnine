from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np

from .scales.scales import Scales
from .utils import match


class Panel(object):
    # n = no. of visual panels
    layout = None     # table n rows, grid information
    shrink = False    # boolean, whether to shrink scales to
                      # fit output of statistics, not raw data
    ranges = None     # list of n dicts.
    x_scales = None   # scale object(s). 1 or n of them
    y_scales  = None  # scale object(s). 1 or n of them

    def train_position(self, data, x_scale, y_scale):
        layout = self.layout
        # Initialise scales if needed, and possible.
        if not self.x_scales and x_scale:
            n = layout['SCALE_X'].max()
            self.x_scales = Scales([x_scale.clone() for i in range(n)])
        if not self.y_scales and y_scale:
            n = layout['SCALE_Y'].max()
            self.y_scales = Scales([y_scale.clone() for i in range(n)])

        # loop over each layer, training x and y scales in turn
        for layer_data in data:
            match_id = match(layer_data['PANEL'], layout['PANEL'])
            if x_scale:
                x_vars = list(set(x_scale.aesthetics) &
                              set(layer_data.columns))
                # the scale index for each data point
                SCALE_X = layout['SCALE_X'].iloc[match_id].tolist()
                self.x_scales.train(layer_data, x_vars, SCALE_X)

            if y_scale:
                y_vars = list(set(y_scale.aesthetics) &
                              set(layer_data.columns))
                # the scale index for each data point
                SCALE_Y = layout['SCALE_Y'].iloc[match_id].tolist()
                self.y_scales.train(layer_data, y_vars, SCALE_Y)

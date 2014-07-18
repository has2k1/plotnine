from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np

class Panel(object):
    # n = no. of visual panels
    layout = None     # table n rows, grid information
    shrink = False    # boolean, whether to shrink scales to
                      # fit output of statistics, not raw data
    ranges = None     # list of n dicts.
    x_scales = None   # scale object(s). 1 or n of them
    y_scales  = None  # scale object(s). 1 or n of them


# def train_layout(panel, facet, layer_data, plot_data):

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pandas as pd


class facet_null(object):

    def __init__(self, shrink=True):
        self.shrink = shrink

    def train_layout(self, data):
        layout = pd.DataFrame({'PANEL': 1, 'ROW': 1, 'COL': 1,
                               'SCALE_X': 1, 'SCALE_Y': 1})
        return layout

    def map_layout(self, data, layout):
        for df in data:
            df['PANEL'] = 1
        return data

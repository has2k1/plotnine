from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from copy import deepcopy

import pandas as pd


class facet_null(object):

    def __init__(self, shrink=True):
        self.shrink = shrink

    def __radd__(self, gg):
        gg = deepcopy(gg)
        gg.facet = self
        return gg

    def train_layout(self, data):
        layout = pd.DataFrame({'PANEL': 1, 'ROW': 1, 'COL': 1,
                               'SCALE_X': 1, 'SCALE_Y': 1},
                              index=[1])
        return layout


    def map_layout(self, layout, data, plot_data):
        """
        Assign a data points to panels

        Parameters
        ----------
        layout : dataframe
            As returned by self.train_layout
        data: list
            dataframe for each layer or None
        plot_data: dataframe
            default data. Specified in the call to  ggplot
        """
        _data = []
        for df in data:
            if df is None:
                df = plot_data.copy()
            df['PANEL'] = 1
            _data.append(df)
        return _data

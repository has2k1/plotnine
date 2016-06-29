from __future__ import absolute_import, division, print_function
from copy import deepcopy

import pandas as pd

from .facet import facet


class facet_null(facet):

    def __init__(self, shrink=True):
        facet.__init__(self, shrink=shrink)
        self.nrow = 1
        self.ncol = 1

    def __radd__(self, gg):
        gg = deepcopy(gg)
        gg.facet = self
        return gg

    def train_layout(self, data):
        layout = pd.DataFrame({'PANEL': 1, 'ROW': 1, 'COL': 1,
                               'SCALE_X': 1, 'SCALE_Y': 1},
                              index=[0])
        return layout

    def map_layout(self, data, layout):
        """
        Assign a data points to panels

        Parameters
        ----------
        data : DataFrame
            dataframe for a layer
        layout : DataFrame
            As returned by self.train_layout
        """
        data['PANEL'] = 1
        return data

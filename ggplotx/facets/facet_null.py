from __future__ import absolute_import, division, print_function
from copy import deepcopy

import pandas as pd

from .facet import facet


class facet_null(facet):
    """
    A single Panel

    Parameters
    ----------
    shrink : bool
        Whether to shrink the scales to the output of the
        statistics instead of the raw data. Default is ``True``.
    """

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

    def set_breaks_and_labels(self, ranges, layout_info, ax):
        """
        Add breaks and labels to the axes

        Parameters
        ----------
        ranges : dict-like
            range information for the axes
        layout_info : dict-like
            facet layout information
        ax : axes
            Axes to decorate.
        """
        facet.set_breaks_and_labels(self, ranges, layout_info, ax)
        ax.xaxis.set_ticks_position('bottom')
        ax.yaxis.set_ticks_position('left')

    def draw_label(self, layout_info, theme, ax):
        pass

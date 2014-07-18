from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pandas as pd
from layouts import layout_grid
from locate import locate_grid


class facet_grid(object):

    def __init__(self, x=None, y=None, margins=False, scales='fixed',
                 space='fixed', shrink=True, labeller='label_value',
                 as_table=True, drop=True):
        # TODO: Implement faceting formula
        self.rows = x
        self.cols = y
        self.margins = margins
        self.shrink = shrink
        self.labeller = labeller
        self.as_table = as_table
        self.drop = drop
        self.free = {'x': scales in ('free_x', 'free'),
                     'y': scales in ('free_y', 'free')}
        self.space_free = {'x': space in ('free_x', 'free'),
                           'y': space in ('free_y', 'free')}


    def train_layout(self, data):
        layout = layout_grid(data, rows=self.rows, cols=self.cols,
                             margins=self.margins, as_table=self.as_table,
                             drop=self.drop)
        # Relax constraints, if necessary
        layout['SCALE_X'] = layout['COL'] if self.free['x'] else 1
        layout['SCALE_Y'] = layout['ROW'] if self.free['y'] else 1

        return layout

    def map_layout(self, data, layout):
        """
        Assign a data points to panels
        """
        _data = []
        for df in data:
            _data.append(locate_grid(df, layout, self.vars))
        return _data

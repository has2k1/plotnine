from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from copy import deepcopy
import re

import six

from ..utils.exceptions import GgplotError
from .layouts import layout_grid
from .locate import locate_grid


class facet_grid(object):

    def __init__(self, facets, margins=False, scales='fixed',
                 space='fixed', shrink=True, labeller='label_value',
                 as_table=True, drop=True):
        self.rows, self.cols = parse_grid_facets(facets)
        self.margins = margins
        self.shrink = shrink
        self.labeller = labeller
        self.as_table = as_table
        self.drop = drop
        self.free = {'x': scales in ('free_x', 'free'),
                     'y': scales in ('free_y', 'free')}
        self.space_free = {'x': space in ('free_x', 'free'),
                           'y': space in ('free_y', 'free')}

    def __radd__(self, gg):
        gg = deepcopy(gg)
        gg.facet = self
        return gg

    def train_layout(self, data):
        layout = layout_grid(data, rows=self.rows, cols=self.cols,
                             margins=self.margins, as_table=self.as_table,
                             drop=self.drop)
        # Relax constraints, if necessary
        layout['SCALE_X'] = layout['COL'] if self.free['x'] else 1
        layout['SCALE_Y'] = layout['ROW'] if self.free['y'] else 1

        self.nrow = layout['ROW'].max()
        self.ncol = layout['COL'].max()
        return layout

    def map_layout(self, data, layout):
        """
        Assign a data points to panels

        Parameters
        ----------
        data : DataFrame
            dataframe for a layer
        layout : dataframe
            As returned by self.train_layout
        """
        return locate_grid(data, layout, self.rows, self.cols,
                           margins=self.margins)


def parse_grid_facets(facets):
    """
    Return two lists of facetting variables, for the rows & columns
    """
    valid_forms = ['var1 ~ .', 'var1 ~ var2', '. ~ var1',
                   'var1 + var2 ~ var3 + var4']
    error_msg = ("'facets' should be a formula string. Valid formula "
                 "look like {}").format(valid_forms)

    if not isinstance(facets, six.string_types):
        raise GgplotError(error_msg)

    variables_pattern = '(\w+(?:\s*\+\s*\w+)*|\.)'
    pattern = '\s*{0}\s*~\s*{0}\s*'.format(variables_pattern)
    match = re.match(pattern, facets)

    if not match:
        raise GgplotError(error_msg)

    lhs = match.group(1)
    rhs = match.group(2)

    if lhs == '.':
        rows = []
    else:
        rows = [var.strip() for var in lhs.split('+')]

    if rhs == '.':
        cols = []
    else:
        cols = [var.strip() for var in rhs.split('+')]

    return rows, cols

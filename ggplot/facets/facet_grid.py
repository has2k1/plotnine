from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from copy import deepcopy
import re

import six

from ..utils.exceptions import GgplotError
from .facet import facet
from .layouts import layout_grid
from .locate import locate_grid


class facet_grid(facet):

    def __init__(self, facets, margins=False, scales='fixed',
                 space='fixed', shrink=True, labeller='label_value',
                 as_table=True, drop=True):
        facet.__init__(
            self, scales=scales, shrink=shrink, labeller=labeller,
            as_table=as_table, drop=drop)
        self.rows, self.cols = parse_grid_facets(facets)
        self.margins = margins
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

    def set_breaks_and_labels(self, ranges, layout_info, ax):
        facet.set_breaks_and_labels(
            self, ranges, layout_info, ax)

        bottomrow = layout_info['ROW'] == self.nrow
        leftcol = layout_info['COL'] == 1

        if bottomrow:
            ax.xaxis.set_ticks_position('bottom')
        else:
            ax.xaxis.set_ticks_position('none')
            ax.xaxis.set_ticklabels([])

        if leftcol:
            ax.yaxis.set_ticks_position('left')
        else:
            ax.yaxis.set_ticks_position('none')
            ax.yaxis.set_ticklabels([])

    def draw_label(self, layout_info, theme, ax):
        """
        Draw facet label onto the axes.

        This function will only draw labels if they are needed.

        Parameters
        ----------
        layout_info : dict-like
            Layout information. Row from the `layout` table.
        theme : theme
            Theme
        ax : axes
            Axes to label
        """
        toprow = layout_info['ROW'] == 1
        rightcol = layout_info['COL'] == self.ncol

        if toprow and len(self.cols):
            label_info = layout_info[list(self.cols)]
            label_info._meta = {'dimension': 'cols'}
            label_info = self.labeller(label_info)
            self.draw_strip_text(label_info, 'top', theme, ax)

        if rightcol and len(self.rows):
            label_info = layout_info[list(self.rows)]
            label_info._meta = {'dimension': 'rows'}
            label_info = self.labeller(label_info)
            self.draw_strip_text(label_info, 'right', theme, ax)


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

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from copy import deepcopy
import re

import six

from ..utils.exceptions import gg_warn, GgplotError
from .facet import facet
from .layouts import layout_wrap
from .locate import locate_wrap


class facet_wrap(facet):

    def __init__(self, facets=None, nrow=None, ncol=None, scales='fixed',
                 shrink=True, labeller='label_value',
                 as_table=True, drop=True):
        facet.__init__(
            self, scales=scales, shrink=shrink, labeller=labeller,
            as_table=as_table, drop=drop)
        self.vars = tuple(parse_wrap_facets(facets))
        self.nrow, self.ncol = check_dimensions(nrow, ncol)

    def __radd__(self, gg):
        gg = deepcopy(gg)
        gg.facet = self
        return gg

    def train_layout(self, data):
        layout = layout_wrap(data, vars=self.vars, nrow=self.nrow,
                             ncol=self.ncol, as_table=self.as_table,
                             drop=self.drop)
        n = layout.shape[0]
        nrow = layout['ROW'].max()

        # Add scale identification
        layout['SCALE_X'] = range(1, n+1) if self.free['x'] else 1
        layout['SCALE_Y'] = range(1, n+1) if self.free['y'] else 1

        # Figure out where axes should go
        layout['AXIS_X'] = True if self.free['x'] else layout['ROW'] == nrow
        layout['AXIS_Y'] = True if self.free['y'] else layout['COL'] == 1

        self.nrow = nrow
        self.ncol = layout['COL'].max()
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
        return locate_wrap(data, layout, self.vars)

    def set_breaks_and_labels(self, ranges, layout_info, ax):
        facet.set_breaks_and_labels(
            self, ranges, layout_info, ax)
        if not layout_info['AXIS_X']:
            ax.xaxis.set_ticks_position('none')
            ax.xaxis.set_ticklabels([])
        if not layout_info['AXIS_Y']:
            ax.yaxis.set_ticks_position('none')
            ax.yaxis.set_ticklabels([])
        if layout_info['AXIS_X']:
            ax.xaxis.set_ticks_position('bottom')
        if layout_info['AXIS_Y']:
            ax.yaxis.set_ticks_position('left')

    def adjust_space(self):
        import matplotlib.pyplot as plt
        hspace = len(self.vars) * .20
        plt.subplots_adjust(wspace=.05, hspace=hspace)

    def draw_label(self, layout_info, theme, ax):
        """
        Draw facet label onto the axes.

        This function will only draw labels if they are needed.

        Parameters
        ----------
        layout_info : dict-like
            facet information
        theme : theme
            Theme
        ax : axes
            Axes to label
        """
        label_info = layout_info[list(self.vars)]
        label_info._meta = {'dimension': 'cols'}
        label_info = self.labeller(label_info)
        self.draw_strip_text(label_info, 'top', theme, ax)


def check_dimensions(nrow, ncol):
    if nrow is not None:
        if nrow < 1:
            gg_warn("'nrow' must be greater than 0. "
                    "Your value has been ignored.")
            nrow = None
        else:
            nrow = int(nrow)

    if ncol is not None:
        if ncol < 1:
            gg_warn("'ncol' must be greater than 0. "
                    "Your value has been ignored.")
            ncol = None
        else:
            ncol = int(ncol)

    return nrow, ncol


def parse_wrap_facets(facets):
    """
    Return list of facetting variables
    """
    valid_forms = ['~ var1', '~ var1 + var2']
    error_msg = ("'facets' should be a formula string. Valid formula "
                 "look like {}").format(valid_forms)

    if isinstance(facets, (list, tuple)):
        return facets

    if not isinstance(facets, six.string_types):
        raise GgplotError(error_msg)

    if '~' in facets:
        variables_pattern = '(\w+(?:\s*\+\s*\w+)*|\.)'
        pattern = '\s*~\s*{0}\s*'.format(variables_pattern)
        match = re.match(pattern, facets)
        if not match:
            raise GgplotError(error_msg)

        facets = [var.strip() for var in match.group(1).split('+')]
    elif re.match('\w+', facets):
        # allow plain string as the variable name
        facets = [facets]
    else:
        raise GgplotError(error_msg)

    return facets

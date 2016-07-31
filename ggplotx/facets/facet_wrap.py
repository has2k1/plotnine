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
    """
    Wrap 1D Panels onto 2D surface

    Parameters
    ----------
    facets : formula | tuple | list
        Variables to groupby and plot on different panels.
        If a formula is used it should be right sided,
        e.g ``'~ a + b'``, ``('a', 'b')``
    nrow : int, optional
        Number of rows
    ncol : int, optional
        Number of columns
    scales : 'fixed' | 'free' | 'free_x' | 'free_y'
        Whether ``x`` or ``y`` scales should be allowed (free)
        to vary according to the data on each of the panel.
        Default is ``'fixed'``.
    shrink : bool
        Whether to shrink the scales to the output of the
        statistics instead of the raw data. Default is ``True``.
    labeller : str | function
        How to label the facets. If it is a ``str``, it should
        be one of ``'label_value'`` ``'label_both'`` or
        ``'label_context'``. Default is ``'label_value'``
    as_table : bool
        If ``True``, the facets are laid out like a table with
        the highest values at the bottom-right. If ``False``
        the facets are laid out like a plot with the highest
        value a the top-right. Default it ``True``.
    drop : bool
        If ``True``, all factor levels not used in the data
        will automatically be dropped. If ``False``, all
        factor levels will be shown, regardless of whether
        or not they appear in the data. Default is ``True``.
    dir : 'h' | 'v'
        Direction in which to layout the panels. ``h`` for
        horizontal and ``v`` for vertical.
    """

    def __init__(self, facets=None, nrow=None, ncol=None, scales='fixed',
                 shrink=True, labeller='label_value',
                 as_table=True, drop=True, dir='h'):
        facet.__init__(
            self, scales=scales, shrink=shrink, labeller=labeller,
            as_table=as_table, drop=drop, dir=dir)
        self.vars = tuple(parse_wrap_facets(facets))
        self.nrow, self.ncol = check_dimensions(nrow, ncol)
        # facet_wrap gets its labelling at the top
        self.num_vars_x = len(self.vars)

    def __radd__(self, gg):
        gg = deepcopy(gg)
        gg.facet = self
        return gg

    def train_layout(self, data):
        layout = layout_wrap(data, vars=self.vars, nrow=self.nrow,
                             ncol=self.ncol, as_table=self.as_table,
                             drop=self.drop, dir=self.dir)
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

    def set_breaks_and_labels(self, ranges, layout_info, pidx):
        ax = self.axs[pidx]
        facet.set_breaks_and_labels(
            self, ranges, layout_info, pidx)
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

    def spaceout_and_resize_panels(self):
        """
        Adjust the spacing between the panels and resize them
        to meet the aspect ratio
        """
        ncol = self.ncol
        nrow = self.nrow
        figure = self.figure
        theme = self.theme
        get_property = theme.themeables.property

        left = figure.subplotpars.left
        right = figure.subplotpars.right
        top = figure.subplotpars.top
        bottom = figure.subplotpars.bottom
        top_strip_height = self.strip_size('top')
        W, H = figure.get_size_inches()

        try:
            marginx = get_property('panel_margin_x')
        except KeyError:
            marginx = 0.1

        try:
            marginy = get_property('panel_margin_y')
        except KeyError:
            marginy = 0.1

        try:
            aspect_ratio = get_property('aspect_ratio')
        except KeyError:
            # If the panels have different limits the coordinates
            # cannot compute a common aspect ratio
            if not self.free['x'] and not self.free['y']:
                aspect_ratio = self.coordinates.aspect(
                    self.panel.ranges[0])

        if theme.themeables.is_blank('strip_text_x'):
            top_strip_height = 0

        # The goal is to have equal spacing along the vertical
        # and the horizontal. We use the wspace and compute
        # the appropriate hspace. It would be a lot easier if
        # MPL had a better layout manager.

        # width of axes and height of axes
        w = ((right-left)*W - marginx*(ncol-1)) / ncol
        h = ((top-bottom)*H - (marginy+top_strip_height)*(nrow-1)) / nrow

        # aspect ratio changes the size of the figure
        if aspect_ratio is not None:
            h = w*aspect_ratio
            H = (h*nrow + (marginy+top_strip_height)*(nrow-1)) / \
                (top-bottom)
            figure.set_figheight(H)

        # spacing
        wspace = marginx/w
        hspace = (marginy + top_strip_height) / h
        figure.subplots_adjust(wspace=wspace, hspace=hspace)

    def draw_label(self, layout_info, ax):
        """
        Draw facet label onto the axes.

        This function will only draw labels if they are needed.

        Parameters
        ----------
        layout_info : dict-like
            facet information
        ax : axes
            Axes to label
        """
        label_info = layout_info[list(self.vars)]
        label_info._meta = {'dimension': 'cols'}
        label_info = self.labeller(label_info)
        self.draw_strip_text(label_info, 'top', ax)


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

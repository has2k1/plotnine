from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import re
from warnings import warn

import numpy as np
import pandas as pd
import six

from ..exceptions import PlotnineError
from ..utils import suppress, match, join_keys
from .facet import facet, combine_vars, layout_null
from .facet import add_missing_facets, eval_facet_vars


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

    def compute_layout(self, data):
        if not self.vars:
            return layout_null()

        base = combine_vars(data, self.plot.environment,
                            self.vars, drop=self.drop)
        n = len(base)
        dims = wrap_dims(n, self.nrow, self.ncol)
        _id = np.arange(1, n+1)

        if self.as_table:
            row = (_id - 1) // dims[1] + 1
        else:
            row = dims[0] - (_id - 1) // dims[1]

        col = (_id - 1) % dims[1] + 1

        if self.dir == 'v':
            row, col = col, row

        layout = pd.DataFrame({'PANEL': pd.Categorical(range(1, n+1)),
                               'ROW': row.astype(int),
                               'COL': col.astype(int)})
        layout = pd.concat([layout, base], axis=1)

        n = layout.shape[0]
        self.nrow = layout['ROW'].max()
        self.ncol = layout['COL'].max()

        # Add scale identification
        layout['SCALE_X'] = range(1, n+1) if self.free['x'] else 1
        layout['SCALE_Y'] = range(1, n+1) if self.free['y'] else 1

        # Figure out where axes should go.
        # The bottom-most row of each column and the left most
        # column of each row
        if self.as_table or self.dir == 'h':
            x_idx = [df['ROW'].idxmax() for _, df in layout.groupby('COL')]
            y_idx = [df['COL'].idxmin() for _, df in layout.groupby('ROW')]
        else:
            x_idx = [df['ROW'].idxmin() for _, df in layout.groupby('COL')]
            y_idx = [df['COL'].idxmax() for _, df in layout.groupby('ROW')]

        layout['AXIS_X'] = False
        layout['AXIS_Y'] = False
        _loc = layout.columns.get_loc
        layout.iloc[x_idx, _loc('AXIS_X')] = True
        layout.iloc[y_idx, _loc('AXIS_Y')] = True

        if self.free['x']:
            layout.loc[:, 'AXIS_X'] = True

        if self.free['y']:
            layout.loc[:, 'AXIS_Y'] = True

        return layout

    def map(self, data, layout):
        if not len(data):
            data['PANEL'] = pd.Categorical(
                [],
                categories=layout['PANEL'].cat.categories,
                ordered=True)
            return data

        facet_vals = eval_facet_vars(data, self.vars, self.plot.environment)
        data, facet_vals = add_missing_facets(data, layout,
                                              self.vars, facet_vals)

        # assign each point to a panel
        keys = join_keys(facet_vals, layout, self.vars)
        data['PANEL'] = match(keys['x'], keys['y'], start=1)
        data = data.sort_values('PANEL', kind='mergesort')

        # matching dtype
        data['PANEL'] = pd.Categorical(
            data['PANEL'],
            categories=layout['PANEL'].cat.categories,
            ordered=True)

        data.reset_index(drop=True, inplace=True)
        return data

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
            spacing_x = get_property('panel_spacing_x')
        except KeyError:
            spacing_x = 0.1

        try:
            spacing_y = get_property('panel_spacing_y')
        except KeyError:
            spacing_y = 0.1

        try:
            aspect_ratio = get_property('aspect_ratio')
        except KeyError:
            # If the panels have different limits the coordinates
            # cannot compute a common aspect ratio
            if not self.free['x'] and not self.free['y']:
                aspect_ratio = self.coordinates.aspect(
                    self.layout.panel_params[0])
            else:
                aspect_ratio = None

        if theme.themeables.is_blank('strip_text_x'):
            top_strip_height = 0

        # Account for the vertical sliding of the strip if any
        with suppress(KeyError):
            strip_margin_x = get_property('strip_margin_x')
            top_strip_height *= (1 + strip_margin_x)

        # The goal is to have equal spacing along the vertical
        # and the horizontal. We use the wspace and compute
        # the appropriate hspace. It would be a lot easier if
        # MPL had a better layout manager.

        # width of axes and height of axes
        w = ((right-left)*W - spacing_x*(ncol-1)) / ncol
        h = ((top-bottom)*H - (spacing_y+top_strip_height)*(nrow-1)) / nrow

        # aspect ratio changes the size of the figure
        if aspect_ratio is not None:
            h = w*aspect_ratio
            H = (h*nrow + (spacing_y+top_strip_height)*(nrow-1)) / \
                (top-bottom)
            figure.set_figheight(H)

        # spacing
        wspace = spacing_x/w
        hspace = (spacing_y + top_strip_height) / h
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
            warn("'nrow' must be greater than 0. "
                 "Your value has been ignored.")
            nrow = None
        else:
            nrow = int(nrow)

    if ncol is not None:
        if ncol < 1:
            warn("'ncol' must be greater than 0. "
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
    error_msg = ("Valid formula for 'facet_wrap' look like"
                 " {}".format(valid_forms))

    if isinstance(facets, (list, tuple)):
        return facets

    if not isinstance(facets, six.string_types):
        raise PlotnineError(error_msg)

    if '~' in facets:
        variables_pattern = r'(\w+(?:\s*\+\s*\w+)*|\.)'
        pattern = r'\s*~\s*{0}\s*'.format(variables_pattern)
        match = re.match(pattern, facets)
        if not match:
            raise PlotnineError(error_msg)

        facets = [var.strip() for var in match.group(1).split('+')]
    elif re.match(r'\w+', facets):
        # allow plain string as the variable name
        facets = [facets]
    else:
        raise PlotnineError(error_msg)

    return facets


def wrap_dims(n, nrow=None, ncol=None):
    if not nrow and not ncol:
        ncol, nrow = n2mfrow(n)
    elif not ncol:
        ncol = int(np.ceil(n/nrow))
    elif not nrow:
        nrow = int(np.ceil(n/ncol))
    if not nrow * ncol >= n:
        raise PlotnineError(
            "Allocated fewer panels than are required. "
            "Make sure the number of rows and columns can "
            "hold all the plot panels.")
    return (nrow, ncol)


def n2mfrow(nr_plots):
    """
    Compute the rows and columns given the number
    of plots.

    This is a port of grDevices::n2mfrow from R
    """
    if nr_plots <= 3:
        nrow, ncol = nr_plots, 1
    elif nr_plots <= 6:
        nrow, ncol = (nr_plots + 1) // 2, 2
    elif nr_plots <= 12:
        nrow, ncol = (nr_plots + 2) // 3, 3
    else:
        nrow = int(np.ceil(np.sqrt(nr_plots)))
        ncol = int(np.ceil(nr_plots/nrow))
    return (nrow, ncol)

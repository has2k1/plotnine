from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import re

import six

from ..utils.exceptions import GgplotError
from .facet import facet
from .layouts import layout_grid
from .locate import locate_grid


class facet_grid(facet):
    """
    Wrap 1D Panels onto 2D surface

    Parameters
    ----------
    facets : formula
        A formula with the rows (of the tabular display) on
        the LHS and the columns (of the tabular display) on
        the RHS; the dot in the formula is used to indicate
        there should be no faceting on this dimension
        (either row or column).
    scales : 'fixed' | 'free' | 'free_x' | 'free_y'
        Whether ``x`` or ``y`` scales should be allowed (free)
        to vary according to the data on each of the panel.
        Default is ``'fixed'``.
    space : 'fixed' | 'free' | 'free_x' | 'free_y'
        Whether the ``x`` or ``y`` sides of the panels
        should have the size. It also depends to the
        ``scales`` parameter. Default is ``'fixed'``.
        This setting is not properly supported at the moment.
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
    """

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
        self.num_vars_x = len(self.cols)
        self.num_vars_y = len(self.rows)

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

    def set_breaks_and_labels(self, ranges, layout_info, pidx):
        ax = self.axs[pidx]
        facet.set_breaks_and_labels(
            self, ranges, layout_info, pidx)

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
        wspace = figure.subplotpars.wspace
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

        # The goal is to have equal spacing along the vertical
        # and the horizontal. We use the wspace and compute
        # the appropriate hspace. It would be a lot easier if
        # MPL had a better layout manager.

        # width of axes and height of axes
        w = ((right-left)*W - marginx*(ncol-1)) / ncol
        h = ((top-bottom)*H - marginy*(nrow-1)) / nrow

        # aspect ratio changes the size of the figure
        if aspect_ratio is not None:
            h = w*aspect_ratio
            H = (h*nrow + marginy*(nrow-1)) / (top-bottom)
            figure.set_figheight(H)

        # spacing
        wspace = marginx/w
        hspace = marginy/h
        figure.subplots_adjust(wspace=wspace, hspace=hspace)

    def draw_label(self, layout_info, ax):
        """
        Draw facet label onto the axes.

        This function will only draw labels if they are needed.

        Parameters
        ----------
        layout_info : dict-like
            Layout information. Row from the `layout` table.
        ax : axes
            Axes to label
        """
        toprow = layout_info['ROW'] == 1
        rightcol = layout_info['COL'] == self.ncol

        if toprow and len(self.cols):
            label_info = layout_info[list(self.cols)]
            label_info._meta = {'dimension': 'cols'}
            label_info = self.labeller(label_info)
            self.draw_strip_text(label_info, 'top', ax)

        if rightcol and len(self.rows):
            label_info = layout_info[list(self.rows)]
            label_info._meta = {'dimension': 'rows'}
            label_info = self.labeller(label_info)
            self.draw_strip_text(label_info, 'right', ax)


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

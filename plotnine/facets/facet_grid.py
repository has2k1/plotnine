import pandas as pd

from ..utils import ninteraction, add_margins, cross_join
from ..utils import match, join_keys
from ..exceptions import PlotnineError
from .facet import facet, layout_null, combine_vars, add_missing_facets
from .facet import eval_facet_vars
from .strips import strip


class facet_grid(facet):
    """
    Wrap 1D Panels onto 2D surface

    Parameters
    ----------
    facets : str | tuple | list
        A formula with the rows (of the tabular display) on
        the LHS and the columns (of the tabular display) on
        the RHS; the dot in the formula is used to indicate
        there should be no faceting on this dimension
        (either row or column). If a tuple/list is used, it
        must of size two, the elements of which must be
        strings or lists. If string formula is not processed
        as you may expect, use tuple/list. For example, the
        follow two specifications are equivalent::

            'func(var4) ~ func(var1+var3) + func(var2)'
            ['func(var4)', ('func(var1+var3)', 'func(var2)')]

        There may be cases where you cannot use a
        use a pure string formula, e.g.::

            ['var4', ('var1+var3', 'var2')]

    margins : bool | list[str]
        variable names to compute margins for.
        True will compute all possible margins.
    scales : str in ``['fixed', 'free', 'free_x', 'free_y']``
        Whether ``x`` or ``y`` scales should be allowed (free)
        to vary according to the data along rows or columns.
        Default is ``'fixed'``, the same scales for all the
        panels.
    space : str | dict
        Control the size of the  ``x`` or ``y`` sides of the panels.
        The size also depends to the ``scales`` parameter.

        If a string, it should be one of
        ``['fixed', 'free', 'free_x', 'free_y']``. Currently, only the
        ``'fixed'`` option is supported.

        Alternatively if a ``dict``, it indicates the relative facet
        size ratios such as::

            {'x': [1, 2], 'y': [3, 1, 1]}

        This means that in the horizontal direction, the second panel
        will be twice the length of the first. In the vertical direction
        the top facet will be the 3 times longer then the second and
        third facets.

        Note that the number of dimensions in the list must equal the
        number of facets that will be produced.

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
            as_table=as_table, drop=drop
        )
        self.space = space
        self.rows, self.cols = parse_grid_facets(facets)
        self.margins = margins
        self.space_free = {
            'x': isinstance(space, str) and space in ('free_x', 'free'),
            'y': isinstance(space, str) and space in ('free_y', 'free')
        }
        self.num_vars_x = len(self.cols)
        self.num_vars_y = len(self.rows)

    def compute_layout(self, data):
        if not self.rows and not self.cols:
            return layout_null()

        base_rows = combine_vars(data, self.plot.environment,
                                 self.rows, drop=self.drop)

        if not self.as_table:
            # Reverse the order of the rows
            base_rows = base_rows[::-1]
        base_cols = combine_vars(data, self.plot.environment,
                                 self.cols, drop=self.drop)

        base = cross_join(base_rows, base_cols)

        if self.margins:
            base = add_margins(base, [self.rows, self.cols], self.margins)
            base = base.drop_duplicates().reset_index(drop=True)

        n = len(base)
        panel = ninteraction(base, drop=True)
        panel = pd.Categorical(panel, categories=range(1, n+1))

        if self.rows:
            rows = ninteraction(base[self.rows], drop=True)
        else:
            rows = 1

        if self.cols:
            cols = ninteraction(base[self.cols], drop=True)
        else:
            cols = 1

        layout = pd.DataFrame({'PANEL': panel,
                               'ROW': rows,
                               'COL': cols})
        layout = pd.concat([layout, base], axis=1)
        layout = layout.sort_values('PANEL')
        layout.reset_index(drop=True, inplace=True)

        # Relax constraints, if necessary
        layout['SCALE_X'] = layout['COL'] if self.free['x'] else 1
        layout['SCALE_Y'] = layout['ROW'] if self.free['y'] else 1
        layout['AXIS_X'] = layout['ROW'] == layout['ROW'].max()
        layout['AXIS_Y'] = layout['COL'] == layout['COL'].min()

        self.nrow = layout['ROW'].max()
        self.ncol = layout['COL'].max()
        return layout

    def map(self, data, layout):
        if not len(data):
            data['PANEL'] = pd.Categorical(
                [],
                categories=layout['PANEL'].cat.categories,
                ordered=True)
            return data

        vars = [x for x in self.rows + self.cols]
        margin_vars = [list(data.columns.intersection(self.rows)),
                       list(data.columns.intersection(self.cols))]
        data = add_margins(data, margin_vars, self.margins)

        facet_vals = eval_facet_vars(data, vars, self.plot.environment)
        data, facet_vals = add_missing_facets(data, layout,
                                              vars, facet_vals)

        # assign each point to a panel
        if len(facet_vals) == 0:
            # Special case of no facetting
            data['PANEL'] = 1
        else:
            keys = join_keys(facet_vals, layout, vars)
            data['PANEL'] = match(keys['x'], keys['y'], start=1)

        # matching dtype and
        # the categories(panel numbers) for the data should be in the
        # same order as the panels. i.e the panels are the reference,
        # they "know" the right order
        data['PANEL'] = pd.Categorical(
            data['PANEL'],
            categories=layout['PANEL'].cat.categories,
            ordered=True)

        data.reset_index(drop=True, inplace=True)
        return data

    def spaceout_and_resize_panels(self):
        """
        Adjust the spacing between the panels

        Resize them to the aspect ratio
        """
        ncol = self.ncol
        nrow = self.nrow
        figure = self.figure
        theme = self.theme
        aspect_ratio = self._aspect_ratio()
        _property = theme.themeables.property

        left = figure.subplotpars.left
        right = figure.subplotpars.right
        top = figure.subplotpars.top
        bottom = figure.subplotpars.bottom
        wspace = figure.subplotpars.wspace
        W, H = figure.get_size_inches()
        spacing_x = _property('panel_spacing_x')
        spacing_y = _property('panel_spacing_y')

        # The goal is to have equal spacing along the vertical
        # and the horizontal. We use the wspace and compute
        # the appropriate hspace. It would be a lot easier if
        # MPL had a better layout manager.

        # width of axes and height of axes
        w = ((right-left)*W - spacing_x*(ncol-1)) / ncol
        h = ((top-bottom)*H - spacing_y*(nrow-1)) / nrow

        # aspect ratio changes the size of the figure
        if aspect_ratio is not None:
            h = w*aspect_ratio
            H = (h*nrow + spacing_y*(nrow-1)) / (top-bottom)
            figure.set_figheight(H)

        # spacing
        wspace = spacing_x/w
        hspace = spacing_y/h
        figure.subplots_adjust(wspace=wspace, hspace=hspace)

    def make_ax_strips(self, layout_info, ax):
        lst = []
        toprow = layout_info['ROW'] == 1
        rightcol = layout_info['COL'] == self.ncol
        if toprow and len(self.cols):
            s = strip(self.cols, layout_info, self, ax, 'top')
            lst.append(s)
        if rightcol and len(self.rows):
            s = strip(self.rows, layout_info, self, ax, 'right')
            lst.append(s)
        return lst


def parse_grid_facets(facets):
    """
    Return two lists of facetting variables, for the rows & columns
    """
    valid_seqs = ["('var1', '.')", "('var1', 'var2')",
                  "('.', 'var1')", "((var1, var2), (var3, var4))"]
    error_msg_s = ("Valid sequences for specifying 'facets' look like"
                   f" {valid_seqs}")

    valid_forms = ['var1 ~ .', 'var1 ~ var2', '. ~ var1',
                   'var1 + var2 ~ var3 + var4',
                   '. ~ func(var1) + func(var2)',
                   '. ~ func(var1+var3) + func(var2)'
                   ] + valid_seqs
    error_msg_f = ("Valid formula for 'facet_grid' look like"
                   f" {valid_forms}")

    if isinstance(facets, (tuple, list)):
        if len(facets) != 2:
            raise PlotnineError(error_msg_s)

        rows, cols = facets

        if isinstance(rows, str):
            rows = [] if rows == '.' else [rows]
        if isinstance(cols, str):
            cols = [] if cols == '.' else [cols]

        return rows, cols

    if not isinstance(facets, str):
        raise PlotnineError(error_msg_f)

    # Example of allowed formulae
    # 'c ~ a + b'
    # '. ~ func(a) + func(b)'
    # 'func(c) ~ func(a+1) + func(b+2)'
    try:
        lhs, rhs = facets.split('~')
    except ValueError:
        raise PlotnineError(error_msg_s)
    else:
        lhs = lhs.strip()
        rhs = rhs.strip()

    lhs = ensure_var_or_dot(lhs)
    rhs = ensure_var_or_dot(rhs)

    lsplitter = ' + ' if ' + ' in lhs else '+'
    rsplitter = ' + ' if ' + ' in rhs else '+'

    if lhs == '.':
        rows = []
    else:
        rows = [var.strip() for var in lhs.split(lsplitter)]

    if rhs == '.':
        cols = []
    else:
        cols = [var.strip() for var in rhs.split(rsplitter)]

    return rows, cols


def ensure_var_or_dot(formula_term):
    """
    Ensure that a non specified formula term is transformed into a dot.
    """
    return formula_term if formula_term else '.'

import itertools
import types
from copy import deepcopy, copy
from contextlib import suppress
from warnings import warn

import numpy as np
import pandas as pd
import pandas.api.types as pdtypes

from .strips import strips
from ..utils import cross_join, match
from ..exceptions import PlotnineError, PlotnineWarning
from ..scales.scales import Scales

# For default matplotlib backend
with suppress(ImportError):
    from matplotlib.ticker import locale, FixedFormatter
    from matplotlib.gridspec import GridSpec


class facet:
    """
    Base class for all facets

    Parameters
    ----------
    scales : str in ``['fixed', 'free', 'free_x', 'free_y']``
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
    dir : str in ``['h', 'v']``
        Direction in which to layout the panels. ``h`` for
        horizontal and ``v`` for vertical.
    """
    #: number of columns
    ncol = None
    #: number of rows
    nrow = None
    as_table = True
    drop = True
    shrink = True
    #: Which axis scales are free
    free = {'x': True, 'y': True}
    #: A dict of parameters created depending on the data
    #: (Intended for extensions)
    params = None
    # Theme object, automatically updated before drawing the plot
    theme = None
    # Figure object on which the facet panels are created
    figure = None
    # coord object, automatically updated before drawing the plot
    coordinates = None
    # layout object, automatically updated before drawing the plot
    layout = None
    # Axes
    axs = None
    # The first and last axes according to how MPL creates them.
    # Used for labelling the x and y axes,
    first_ax = None
    last_ax = None
    # Number of facet variables along the horizontal axis
    num_vars_x = 0
    # Number of facet variables along the vertical axis
    num_vars_y = 0
    # ggplot object that the facet belongs to
    plot = None
    # Facet strips
    strips = None
    # Control the relative size of multiple facets
    # Use a subclass to change the default.
    # See: facet_grid for an example
    space = 'fixed'

    def __init__(self, scales='fixed', shrink=True,
                 labeller='label_value', as_table=True,
                 drop=True, dir='h'):
        from .labelling import as_labeller
        self.shrink = shrink
        self.labeller = as_labeller(labeller)
        self.as_table = as_table
        self.drop = drop
        self.dir = dir
        self.free = {'x': scales in ('free_x', 'free'),
                     'y': scales in ('free_y', 'free')}

    def __radd__(self, gg, inplace=False):
        """
        Add facet to ggplot object
        """
        gg = gg if inplace else deepcopy(gg)
        gg.facet = copy(self)
        gg.facet.plot = gg
        return gg

    def set(self, **kwargs):
        """
        Set properties
        """
        for name, value in kwargs.items():
            if hasattr(self, name):
                setattr(self, name, value)
            else:
                raise AttributeError(
                    f"{self.__class__.__name__} object has "
                    f"no attribute {name}"
                )

    def setup_data(self, data):
        """
        Allow the facet to manipulate the data

        Parameters
        ----------
        data : list of dataframes
            Data for each of the layers

        Returns
        -------
        data : list of dataframes
            Data for each of the layers

        Notes
        -----
        This method will be called after :meth:`setup_params`,
        therefore the `params` property will be set.
        """
        return data

    def setup_params(self, data):
        """
        Create facet parameters

        Parameters
        ----------
        data : list of dataframes
            Plot data and data for the layers
        """
        self.params = {}

    def init_scales(self, layout, x_scale=None, y_scale=None):
        scales = types.SimpleNamespace()

        if x_scale is not None:
            n = layout['SCALE_X'].max()
            scales.x = Scales([x_scale.clone() for i in range(n)])

        if y_scale is not None:
            n = layout['SCALE_Y'].max()
            scales.y = Scales([y_scale.clone() for i in range(n)])

        return scales

    def map(self, data, layout):
        """
        Assign a data points to panels

        Parameters
        ----------
        data : DataFrame
            Data for a layer
        layout : DataFrame
            As returned by self.compute_layout

        Returns
        -------
        data : DataFrame
            Data with all points mapped to the panels
            on which they will be plotted.
        """
        msg = "{} should implement this method."
        raise NotImplementedError(
            msg.format(self.__class.__name__))

    def compute_layout(self, data):
        """
        Compute layout
        """
        msg = "{} should implement this method."
        raise NotImplementedError(
            msg.format(self.__class.__name__))

    def finish_data(self, data, layout):
        """
        Modify data before it is drawn out by the geom

        The default is to return the data without modification.
        Subclasses should override this method as the require.

        Parameters
        ----------
        data : DataFrame
            Layer data.
        layout : Layout
            Layout

        Returns
        -------
        data : DataFrame
            Modified layer data
        """
        return data

    def train_position_scales(self, layout, layers):
        """
        Compute ranges for the x and y scales
        """
        _layout = layout.layout
        panel_scales_x = layout.panel_scales_x
        panel_scales_y = layout.panel_scales_y

        # loop over each layer, training x and y scales in turn
        for layer in layers:
            data = layer.data
            match_id = match(data['PANEL'], _layout['PANEL'])
            if panel_scales_x:
                x_vars = list(set(panel_scales_x[0].aesthetics) &
                              set(data.columns))
                # the scale index for each data point
                SCALE_X = _layout['SCALE_X'].iloc[match_id].tolist()
                panel_scales_x.train(data, x_vars, SCALE_X)

            if panel_scales_y:
                y_vars = list(set(panel_scales_y[0].aesthetics) &
                              set(data.columns))
                # the scale index for each data point
                SCALE_Y = _layout['SCALE_Y'].iloc[match_id].tolist()
                panel_scales_y.train(data, y_vars, SCALE_Y)

        return self

    def make_ax_strips(self, layout_info, ax):
        """
        Create strips for the facet

        Parameters
        ----------
        layout_info : dict-like
            Layout information. Row from the layout table

        ax : axes
            Axes to label
        """
        return []

    def initialise_strips(self):
        """
        Initialise strips for the facet
        """
        self.strips = strips.initialise(self)

    def set_limits_breaks_and_labels(self, panel_params, ax):
        # limits
        ax.set_xlim(panel_params.x.range)
        ax.set_ylim(panel_params.y.range)

        # breaks, labels
        ax.set_xticks(panel_params.x.breaks, panel_params.x.labels)
        ax.set_yticks(panel_params.y.breaks, panel_params.y.labels)

        # minor breaks
        ax.set_xticks(panel_params.x.minor_breaks, minor=True)
        ax.set_yticks(panel_params.y.minor_breaks, minor=True)

        # When you manually set the tick labels MPL changes the locator
        # so that it no longer reports the x & y positions
        # Fixes https://github.com/has2k1/plotnine/issues/187
        ax.xaxis.set_major_formatter(MyFixedFormatter(panel_params.x.labels))
        ax.yaxis.set_major_formatter(MyFixedFormatter(panel_params.y.labels))

        _property = self.theme.themeables.property
        margin = _property('axis_text_x', 'margin')
        pad_x = margin.get_as('t', 'pt')

        margin = _property('axis_text_y', 'margin')
        pad_y = margin.get_as('r', 'pt')

        ax.tick_params(axis='x', which='major', pad=pad_x)
        ax.tick_params(axis='y', which='major', pad=pad_y)

    def __deepcopy__(self, memo):
        """
        Deep copy without copying the dataframe and environment
        """
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        old = self.__dict__
        new = result.__dict__

        # don't make a deepcopy of the figure & the axes
        shallow = {'figure', 'axs', 'first_ax', 'last_ax'}
        for key, item in old.items():
            if key in shallow:
                new[key] = old[key]
                memo[id(new[key])] = new[key]
            else:
                new[key] = deepcopy(old[key], memo)

        return result

    def _create_subplots(self, fig, layout):
        """
        Create suplots and return axs
        """
        num_panels = len(layout)
        axsarr = np.empty((self.nrow, self.ncol), dtype=object)
        space = self.space
        default_space = {
            'x': [1 for x in range(self.ncol)],
            'y': [1 for x in range(self.nrow)],
        }

        if isinstance(space, str):
            if space == 'fixed':
                space = default_space
            # TODO: Implement 'free', 'free_x' & 'free_y'
            else:
                space = default_space
        elif isinstance(space, dict):
            if 'x' not in space:
                space['x'] = default_space['x']
            if 'y' not in space:
                space['y'] = default_space['y']

        if len(space['x']) != self.ncol:
            raise ValueError(
                "The number of x-ratios for the facet space sizes "
                "should match the number of columns."
            )

        if len(space['y']) != self.nrow:
            raise ValueError(
                "The number of y-ratios for the facet space sizes "
                "should match the number of rows."
            )

        gs = GridSpec(
            self.nrow,
            self.ncol,
            height_ratios=space['y'],
            width_ratios=space['x']
        )

        # Create axes
        i = 1
        for row in range(self.nrow):
            for col in range(self.ncol):
                axsarr[row, col] = fig.add_subplot(gs[i - 1])
                i += 1

        # Rearrange axes
        # They are ordered to match the positions in the layout table
        if self.dir == 'h':
            order = 'C'
            if not self.as_table:
                axsarr = axsarr[::-1]
        elif self.dir == 'v':
            order = 'F'
            if not self.as_table:
                axsarr = np.array([row[::-1] for row in axsarr])

        axs = axsarr.ravel(order)

        # Delete unused axes
        for ax in axs[num_panels:]:
            fig.delaxes(ax)
        axs = axs[:num_panels]
        return axs

    def make_axes(self, figure, layout, coordinates):
        """
        Create and return Matplotlib axes
        """
        axs = self._create_subplots(figure, layout)

        # Used for labelling the x and y axes, the first and
        # last axes according to how MPL creates them.
        self.first_ax = figure.axes[0]
        self.last_ax = figure.axes[-1]
        self.figure = figure
        self.axs = axs
        return axs

    def _aspect_ratio(self):
        """
        Return the aspect_ratio
        """
        aspect_ratio = self.theme.themeables.property('aspect_ratio')
        if aspect_ratio == 'auto':
            # If the panels have different limits the coordinates
            # cannot compute a common aspect ratio
            if not self.free['x'] and not self.free['y']:
                aspect_ratio = self.coordinates.aspect(
                    self.layout.panel_params[0]
                )
            else:
                aspect_ratio = None

        return aspect_ratio

    def spaceout_and_resize_panels(self):
        """
        Adjust the spacing between the panels

        Resize them to meet the aspect ratio
        """
        pass

    def check_axis_text_space(self):
        _adjust = self.theme.themeables.get('subplots_adjust')
        if _adjust:
            has_wspace = 'wspace' in _adjust.properties['value']
            has_hspace = 'hspace' in _adjust.properties['value']
        else:
            has_wspace = False
            has_hspace = False

        warn_x = self.ncol > 1 and self.free['y'] and not has_wspace
        warn_y = self.nrow > 1 and self.free['x'] and not has_hspace

        if warn_x:
            warn("If you need more space for the x-axis tick text use "
                 "... + theme(subplots_adjust={'wspace': 0.25}). "
                 "Choose an appropriate value for 'wspace'.",
                 PlotnineWarning
                 )
        if warn_y:
            warn("If you need more space for the y-axis tick text use "
                 "... + theme(subplots_adjust={'hspace': 0.25}). "
                 "Choose an appropriate value for 'hspace'",
                 PlotnineWarning
                 )


def combine_vars(data, environment=None, vars=None, drop=True):
    """
    Generate all combinations of data needed for facetting

    The first data frame in the list should be the default data
    for the plot. Other data frames in the list are ones that are
    added to the layers.
    """
    if not vars:
        return pd.DataFrame()

    # For each layer, compute the facet values
    values = [
        eval_facet_vars(df, vars, environment)
        for df in data if df is not None
    ]

    # Form the base data frame which contains all combinations
    # of facetting variables that appear in the data
    has_all = [x.shape[1] == len(vars) for x in values]
    if not any(has_all):
        raise PlotnineError(
            "At least one layer must contain all variables "
            "used for facetting"
        )
    base = pd.concat([x for i, x in enumerate(values) if has_all[i]],
                     axis=0)
    base = base.drop_duplicates()

    if not drop:
        base = unique_combs(base)

    # sorts according to order of factor levels
    base = base.sort_values(list(base.columns))

    # Systematically add on missing combinations
    for i, value in enumerate(values):
        if has_all[i] or len(value.columns) == 0:
            continue
        old = base.loc[:, base.columns.difference(value.columns)]
        new = value.loc[
            :,
            base.columns.intersection(value.columns)
        ].drop_duplicates()
        if not drop:
            new = unique_combs(new)
        base = pd.concat(base, cross_join(old, new), ignore_index=True)

    if len(base) == 0:
        raise PlotnineError(
            "Faceting variables must have at least one value"
        )

    base = base.reset_index(drop=True)
    return base


def unique_combs(df):
    """
    Generate all possible combinations of the values in the columns
    """
    def _unique(s):
        if isinstance(s.dtype, pdtypes.CategoricalDtype):
            return s.cat.categories
        return s.unique()

    # List of unique values from every column
    lst = (_unique(x) for _, x in df.iteritems())
    rows = list(itertools.product(*lst))
    _df = pd.DataFrame(rows, columns=df.columns)

    # preserve the column dtypes
    for col in df:
        _df[col] = _df[col].astype(df[col].dtype, copy=False)
    return _df


def layout_null():
    """
    Layout Null
    """
    layout = pd.DataFrame({
        'PANEL': 1, 'ROW': 1, 'COL': 1,
        'SCALE_X': 1, 'SCALE_Y': 1,
        'AXIS_X': True, 'AXIS_Y': True
    }, index=[0])
    return layout


def add_missing_facets(data, layout, vars, facet_vals):
    """
    Add missing facets
    """
    # When in a dataframe some layer does not have all
    # the facet variables, add the missing facet variables
    # and create new data where the points(duplicates) are
    # present in all the facets
    missing_facets = list(set(vars) - set(facet_vals))
    if missing_facets:
        to_add = layout.loc[:, missing_facets].drop_duplicates()
        to_add.reset_index(drop=True, inplace=True)

        # a point for each facet, [0, 1, ..., n-1, 0, 1, ..., n-1, ...]
        data_rep = np.tile(np.arange(len(data)), len(to_add))
        # a facet for each point, [0, 0, 0, 1, 1, 1, ... n-1, n-1, n-1]
        facet_rep = np.repeat(np.arange(len(to_add)), len(data))

        data = data.iloc[data_rep, :].reset_index(drop=True)
        facet_vals = facet_vals.iloc[data_rep, :].reset_index(drop=True)
        to_add = to_add.iloc[facet_rep, :].reset_index(drop=True)
        facet_vals = pd.concat([facet_vals, to_add],
                               axis=1, ignore_index=False)

    return data, facet_vals


def eval_facet_vars(data, vars, env):
    """
    Evaluate facet variables

    Parameters
    ----------
    data : DataFrame
        Factet dataframe
    vars : list
        Facet variables
    env : environment
        Plot environment

    Returns
    -------
    facet_vals : DataFrame
        Facet values that correspond to the specified
        variables.
    """
    # To allow expressions in facet formula
    def I(value):
        return value

    env = env.with_outer_namespace({'I': I})
    facet_vals = pd.DataFrame(index=data.index)

    for name in vars:
        if name in data:
            # This is a limited solution. If a keyword is
            # part of an expression it will fail in the
            # else statement below
            res = data[name]
        elif str.isidentifier(name):
            # All other non-statements
            continue
        else:
            # Statements
            try:
                res = env.eval(name, inner_namespace=data)
            except NameError:
                continue
        facet_vals[name] = res

    return facet_vals


class MyFixedFormatter(FixedFormatter):
    """
    Override MPL fixedformatter for better formatting
    """

    def format_data(self, value):
        """
        Return a formatted string representation of a number.
        """
        s = locale.format_string('%1.10e', (value,))
        return self.fix_minus(s)

from copy import deepcopy, copy
import itertools
from contextlib import suppress
from warnings import warn

import numpy as np
import pandas as pd
import types

from ..utils import cross_join, match
from ..exceptions import PlotnineError, PlotnineWarning
from ..scales.scales import Scales

# For default matplotlib backend
with suppress(ImportError):
    import matplotlib.text as mtext
    import matplotlib.patches as mpatch
    from matplotlib.ticker import locale, FixedFormatter


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
                    "{!r} object has no attribute {}".format(
                        self.__class__.__name__,
                        name))

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

    def set_limits_breaks_and_labels(self, panel_params, ax):
        # limits
        ax.set_xlim(panel_params.x.range)
        ax.set_ylim(panel_params.y.range)

        # breaks
        ax.set_xticks(panel_params.x.breaks)
        ax.set_yticks(panel_params.y.breaks)

        # minor breaks
        ax.set_xticks(panel_params.x.minor_breaks, minor=True)
        ax.set_yticks(panel_params.y.minor_breaks, minor=True)

        # labels
        ax.set_xticklabels(panel_params.x.labels)
        ax.set_yticklabels(panel_params.y.labels)

        # When you manually set the tick labels MPL changes the locator
        # so that it no longer reports the x & y positions
        # Fixes https://github.com/has2k1/plotnine/issues/187
        ax.xaxis.set_major_formatter(MyFixedFormatter(panel_params.x.labels))
        ax.yaxis.set_major_formatter(MyFixedFormatter(panel_params.y.labels))

        get_property = self.theme.themeables.property
        # Padding between ticks and text
        try:
            margin = get_property('axis_text_x', 'margin')
        except KeyError:
            pad_x = 2.4
        else:
            pad_x = margin.get_as('t', 'pt')

        try:
            margin = get_property('axis_text_y', 'margin')
        except KeyError:
            pad_y = 2.4
        else:
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

        # Create axes
        i = 1
        for row in range(self.nrow):
            for col in range(self.ncol):
                axsarr[row, col] = fig.add_subplot(self.nrow, self.ncol, i)
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

    def spaceout_and_resize_panels(self):
        """
        Adjust the spacing between the panels and resize them
        to meet the aspect ratio
        """
        pass

    def inner_strip_margins(self, location):
        if location == 'right':
            strip_name = 'strip_text_y'
            side1, side2 = 'l', 'r'
        else:
            strip_name = 'strip_text_x'
            side1, side2 = 't', 'b'

        try:
            margin = self.theme.themeables.property(
                strip_name, 'margin')
        except KeyError:
            m1, m2 = 3, 3
        else:
            m1 = margin.get_as(side1, 'pt')
            m2 = margin.get_as(side2, 'pt')

        return m1, m2

    def strip_size(self, location='top', num_lines=None):
        """
        Breadth of the strip background in inches

        Parameters
        ----------
        location : str in ``['top', 'right']``
            Location of the strip text
        num_lines : int
            Number of text lines
        """
        dpi = 72
        theme = self.theme
        get_property = theme.themeables.property

        if location == 'right':
            strip_name = 'strip_text_y'
            num_lines = num_lines or self.num_vars_y
        else:
            strip_name = 'strip_text_x'
            num_lines = num_lines or self.num_vars_x

        if not num_lines:
            return 0

        # The facet labels are placed onto the figure using
        # transAxes dimensions. The line height and line
        # width are mapped to the same [0, 1] range
        # i.e (pts) * (inches / pts) * (1 / inches)
        try:
            fontsize = get_property(strip_name, 'size')
        except KeyError:
            fontsize = float(theme.rcParams.get('font.size', 10))

        try:
            linespacing = get_property(strip_name, 'linespacing')
        except KeyError:
            linespacing = 1

        # margins on either side of the strip text
        m1, m2 = self.inner_strip_margins(location)
        # Using figure.dpi value here does not workout well!
        breadth = (linespacing*fontsize) * num_lines / dpi
        breadth = breadth + (m1 + m2) / dpi
        return breadth

    def strip_dimensions(self, text_lines, location, ax):
        """
        Calculate the dimension

        Returns
        -------
        out : types.SimpleNamespace
            A structure with all the coordinates required
            to draw the strip text and the background box.
        """
        dpi = 72
        num_lines = len(text_lines)
        get_property = self.theme.themeables.property
        bbox = ax.get_window_extent().transformed(
            self.figure.dpi_scale_trans.inverted())
        ax_width, ax_height = bbox.width, bbox.height  # in inches
        strip_size = self.strip_size(location, num_lines)
        m1, m2 = self.inner_strip_margins(location)
        m1, m2 = m1/dpi, m2/dpi
        margin = 0  # default

        if location == 'right':
            box_x = 1
            box_y = 0
            box_width = strip_size/ax_width
            box_height = 1
            # y & height properties of the background slide and
            # shrink the strip vertically. The y margin slides
            # it horizontally.
            with suppress(KeyError):
                box_y = get_property('strip_background_y', 'y')
            with suppress(KeyError):
                box_height = get_property('strip_background_y', 'height')
            with suppress(KeyError):
                margin = get_property('strip_margin_y')
            x = 1 + (strip_size-m2+m1) / (2*ax_width)
            y = (2*box_y+box_height)/2
            # margin adjustment
            hslide = 1 + margin*strip_size/ax_width
            x *= hslide
            box_x *= hslide
        else:
            box_x = 0
            box_y = 1
            box_width = 1
            box_height = strip_size/ax_height
            # x & width properties of the background slide and
            # shrink the strip horizontally. The y margin slides
            # it vertically.
            with suppress(KeyError):
                box_x = get_property('strip_background_x', 'x')
            with suppress(KeyError):
                box_width = get_property('strip_background_x', 'width')
            with suppress(KeyError):
                margin = get_property('strip_margin_x')
            x = (2*box_x+box_width)/2
            y = 1 + (strip_size-m1+m2)/(2*ax_height)
            # margin adjustment
            vslide = 1 + margin*strip_size/ax_height
            y *= vslide
            box_y *= vslide

        dimensions = types.SimpleNamespace(
            x=x, y=y, box_x=box_x, box_y=box_y,
            box_width=box_width,
            box_height=box_height)
        return dimensions

    def draw_strip_text(self, text_lines, location, ax):
        """
        Create a background patch and put a label on it
        """
        themeable = self.figure._themeable
        dim = self.strip_dimensions(text_lines, location, ax)

        if location == 'right':
            rotation = -90
            label = '\n'.join(reversed(text_lines))
        else:
            rotation = 0
            label = '\n'.join(text_lines)

        rect = mpatch.FancyBboxPatch((dim.box_x, dim.box_y),
                                     width=dim.box_width,
                                     height=dim.box_height,
                                     facecolor='lightgrey',
                                     edgecolor='None',
                                     transform=ax.transAxes,
                                     zorder=2.2,  # > ax line & boundary
                                     boxstyle='square, pad=0',
                                     clip_on=False)

        text = mtext.Text(dim.x, dim.y, label,
                          rotation=rotation,
                          verticalalignment='center',
                          horizontalalignment='center',
                          transform=ax.transAxes,
                          zorder=3.3,  # > rect
                          clip_on=False)

        ax.add_artist(rect)
        ax.add_artist(text)

        for key in ('strip_text_x', 'strip_text_y',
                    'strip_background_x', 'strip_background_y'):
            if key not in themeable:
                themeable[key] = []

        if location == 'right':
            themeable['strip_background_y'].append(rect)
            themeable['strip_text_y'].append(text)
        else:
            themeable['strip_background_x'].append(rect)
            themeable['strip_text_x'].append(text)

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
    Base layout function that generates all combinations of data
    needed for facetting
    The first data frame in the list should be the default data
    for the plot. Other data frames in the list are ones that are
    added to the layers.
    """
    if not vars:
        return pd.DataFrame()

    # For each layer, compute the facet values
    values = [eval_facet_vars(df, vars, environment)
              for df in data if df is not None]

    # Form the base data frame which contains all combinations
    # of facetting variables that appear in the data
    has_all = [x.shape[1] == len(vars) for x in values]
    if not any(has_all):
        raise PlotnineError(
            "At least one layer must contain all variables " +
            "used for facetting")
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
        old = base.loc[:, base.columns - value.columns]
        new = value.loc[:, base.columns & value.columns].drop_duplicates()
        if not drop:
            new = unique_combs(new)
        base = base.append(cross_join(old, new), ignore_index=True)

    if len(base) == 0:
        raise PlotnineError(
            "Faceting variables must have at least one value")

    base = base.reset_index(drop=True)
    return base


def unique_combs(df):
    """
    Return data frame with all possible combinations
    of the values in the columns
    """
    # List of unique values from every column
    lst = (x.unique() for x in (df[c] for c in df))
    rows = list(itertools.product(*lst))
    _df = pd.DataFrame(rows, columns=df.columns)

    # preserve the column dtypes
    for col in df:
        _df[col] = _df[col].astype(df[col].dtype, copy=False)
    return _df


def layout_null():
    layout = pd.DataFrame({'PANEL': 1, 'ROW': 1, 'COL': 1,
                           'SCALE_X': 1, 'SCALE_Y': 1,
                           'AXIS_X': True, 'AXIS_Y': True},
                          index=[0])
    return layout


def add_missing_facets(data, layout, vars, facet_vals):
    # When in a dataframe some layer does not have all
    # the facet variables, add the missing facet variables
    # and create new data where the points(duplicates) are
    # present in all the facets
    missing_facets = set(vars) - set(facet_vals)
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
    def format_data(self, value):
        """
        Return a formatted string representation of a number.
        """
        s = locale.format_string('%1.10e', (value,))
        return self.fix_minus(s)

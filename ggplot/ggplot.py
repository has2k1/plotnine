from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import sys
from copy import deepcopy

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnchoredOffsetbox
import matplotlib.text as mtext
import matplotlib.patches as mpatch
from six.moves import zip

from .components.aes import make_labels
from .components.panel import Panel
from .components.layer import Layers
from .facets import facet_null, facet_grid, facet_wrap
from .themes.theme_gray import theme_gray
from .utils import is_waive, suppress
from .utils.ggutils import gg_context, ggplot_options
from .scales.scales import Scales
from .scales.scales import scales_add_missing
from .coords import coord_cartesian
from .guides.guides import guides
from .geoms import geom_blank


# Show plots if in interactive mode
if sys.flags.interactive:
    plt.ion()


class ggplot(object):
    """
    ggplot is the base layer or object that you use to define
    the components of your chart (x and y axis, shapes, colors, etc.).
    You can combine it with layers (or geoms) to make complex graphics
    with minimal effort.

    Parameters
    -----------
    aesthetics :  aes (ggplot.components.aes.aes)
        aesthetics of your plot
    data :  pandas DataFrame (pd.DataFrame)
        a DataFrame with the data you want to plot

    Examples
    ----------
    >>> p = ggplot(aes(x='x', y='y'), data=diamonds)
    >>> print(p + geom_point())
    """

    CONTINUOUS = ['x', 'y', 'size', 'alpha']
    DISCRETE = ['color', 'shape', 'marker', 'alpha', 'linestyle']

    def __init__(self, mapping, data):
        if not isinstance(data, pd.DataFrame):
            mapping, data = data, mapping

        self.data = data
        self.mapping = mapping
        self.facet = facet_null()
        self.labels = make_labels(mapping)
        self.layers = Layers()
        self.guides = guides()
        self.scales = Scales()
        # default theme is theme_gray
        self.theme = theme_gray()
        self.coordinates = coord_cartesian()
        self.plot_env = mapping.aes_env
        self.panel = None

    def __repr__(self):
        """Print/show the plot"""
        # We're going to default to making the plot appear
        # when __repr__ is called.
        self.draw()
        plt.show()
        # TODO: We can probably get more sugary with this
        return "<ggplot: (%d)>" % self.__hash__()

    def __deepcopy__(self, memo):
        """
        Deep copy without copying the dataframe and environment
        """
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result

        # don't make a deepcopy of data, or plot_env
        shallow = {'data', 'plot_env'}
        for key, item in self.__dict__.items():
            if key in shallow:
                result.__dict__[key] = self.__dict__[key]
            else:
                result.__dict__[key] = deepcopy(self.__dict__[key], memo)

        return result

    def _make_axes(self, plot):
        """
        Create MPL figure and axes

        Parameters
        ----------
        plot : ggplot
            built ggplot object

        Note
        ----
        This method creates a grid of axes and
        unsed ones are turned off.
        A dict `figure._themeable` is attached to
        the figure to get a handle on objects that
        may be themed
        """
        figure, axs = plt.subplots(plot.facet.nrow,
                                   plot.facet.ncol,
                                   sharex=False,
                                   sharey=False)
        figure._themeable = {}
        try:
            axs = axs.flatten()
        except AttributeError:
            axs = [axs]

        for ax in axs[len(plot.panel.layout):]:
            ax.axis('off')
        axs = axs[:len(plot.panel.layout)]

        plot.axs = plot.panel.axs = axs
        plot.figure = plot.theme.figure = figure

    def draw(self):
        """
        Render the complete plot and return the matplotlib figure
        """
        if ggplot_options['close_all_figures']:
            plt.close("all")

        with gg_context(theme=self.theme):
            plot = self.draw_plot()
            plot = self.draw_legend(plot)
            # Theming
            for ax in plot.axs:
                plot.theme.apply(ax)

        return plot.figure

    def draw_plot(self):
        """
        Draw the main plot(s) onto the axes.

        Return
        ------
        out : ggplot
            ggplot object with two new properties
                - axs
                - figure
        """
        data, plot = self.build()
        self._make_axes(plot)
        panel = plot.panel

        # Draw the geoms
        for l, ldata in zip(plot.layers, data):
            l.draw(ldata, panel, plot.coordinates)

        # Decorate the axes
        #   - xaxis & yaxis breaks, labels, limits, ...
        #   - facet labels
        #
        # ploc is the panel location (left to right, top to bottom)
        for ploc, finfo in panel.layout.iterrows():
            panel_scales = panel.ranges[ploc]
            ax = panel.axs[ploc]
            set_breaks_and_labels(plot, panel_scales, finfo, ax)
            draw_facet_label(plot, finfo, ax)

        apply_facet_spacing(plot)
        add_labels_and_title(plot)

        return plot

    def build(self):
        """
        Build ggplot for rendering.

        This function takes the plot object, and performs all steps
        necessary to produce an object that can be rendered.

        Returns
        -------
        data : list
            dataframes, one for each layer
        panel : panel
            panel object with all the finformation required
            for ploting
        plot : ggplot
            A copy of the ggplot object
        """
        plot = deepcopy(self)

        if not plot.layers:
            plot += geom_blank()

        plot.panel = Panel()
        layers = plot.layers
        layer_data = [l.data for l in layers]
        scales = plot.scales
        panel = plot.panel

        # Initialise panels, add extra data for margins & missing
        # facetting variables, and add on a PANEL variable to data
        panel.train_layout(plot.facet, layer_data, plot.data)
        data = panel.map_layout(plot.facet, layer_data, plot.data)

        # Compute aesthetics to produce data with generalised variable names
        data = [l.compute_aesthetics(d, plot) for l, d in zip(layers, data)]

        # Transform data using all scales
        data = [scales.transform_df(d) for d in data]

        # Map and train positions so that statistics have access
        # to ranges and all positions are numeric
        def scale_x():
            return scales.get_scales('x')

        def scale_y():
            return scales.get_scales('y')

        panel.train_position(data, scale_x(), scale_y())
        data = panel.map_position(data, scale_x(), scale_y())

        # Apply and map statistics
        data = [l.compute_statistic(d, panel)
                for l, d in zip(layers, data)]
        data = [l.map_statistic(d, plot) for l, d in zip(layers, data)]

        # Make sure missing (but required) aesthetics are added
        scales_add_missing(plot, ('x', 'y'))

        # Prepare data in geoms from (e.g.) y and width to ymin and ymax
        data = [l.setup_data(d) for l, d in zip(layers, data)]

        # Apply position adjustments
        data = [l.compute_position(d, panel)
                for l, d in zip(layers, data)]

        # Reset position scales, then re-train and map.  This ensures
        # that facets have control over the range of a plot:
        #   - is it generated from what's displayed, or
        #   - does it include the range of underlying data
        panel.reset_scales()
        panel.train_position(data, scale_x(), scale_y())
        data = panel.map_position(data, scale_x(), scale_y())

        # Train and map non-position scales
        npscales = scales.non_position_scales()
        if len(npscales):
            data = [npscales.train_df(d) for d in data]
            data = [npscales.map_df(d) for d in data]

        # Train coordinate system
        panel.train_ranges(plot.coordinates)

        # fill in the defaults
        data = [l.use_defaults(d) for l, d in zip(layers, data)]

        return data, plot

    def draw_legend(self, plot):
        legend_box = plot.guides.build(plot)
        if not legend_box:
            return plot

        position = plot.theme._params['legend_position']
        # At what point (e.g [.94, .5]) on the figure
        # to place which point (e.g 6, for center left) of
        # the legend box
        lookup = {
            'right':  (6, (0.92, 0.5)),  # center left
            'left': (7, (0.07, 0.5)),    # center right
            'top': (8, (0.5, 0.92)),     # bottom center
            'bottom': (9, (0.5, 0.07))   # upper center
        }
        loc, box_to_anchor = lookup[position]
        anchored_box = AnchoredOffsetbox(
            loc=loc,
            child=legend_box,
            pad=0.,
            frameon=False,
            # Spacing goes here
            bbox_to_anchor=box_to_anchor,
            bbox_transform=plot.figure.transFigure,
            borderpad=0.,
        )
        plot.figure._themeable['legend_background'] = anchored_box
        ax = plot.axs[0]
        ax.add_artist(anchored_box)
        return plot


def set_breaks_and_labels(plot, ranges, finfo, ax):
    """
    Set the limits, breaks and labels for the axis

    Parameters
    ----------
    plot : ggplot
        ggplot object
    ranges : dict-like
        range information for the axes
    finfo : dict-like
        facet layout information
    ax : axes
        current axes
    """
    # It starts out with axes and labels on
    # all sides, we keep what we want and
    # get rid of what we don't want depending
    # on the plot

    # limits
    ax.set_xlim(ranges['x_range'])
    ax.set_ylim(ranges['y_range'])

    # breaks and labels for when the user set
    # them explicitly
    def setter(ax_set_method, value, **kwargs):
        """Call axes set method if value is available"""
        if not is_waive(value) and value is not None:
            ax_set_method(value, **kwargs)

    setter(ax.set_xticks, ranges['x_major'])
    setter(ax.set_yticks, ranges['y_major'])
    setter(ax.set_xticks, ranges['x_minor'], minor=True)
    setter(ax.set_yticks, ranges['y_minor'], minor=True)
    setter(ax.set_xticklabels, ranges['x_labels'])
    setter(ax.set_yticklabels, ranges['y_labels'])

    # Add axis Locators and Formatters for when
    # the mpl deals with the breaks and labels
    pscales = plot.scales.position_scales()
    for sc in pscales:
        with suppress(AttributeError):
            sc.trans.modify_axis(ax)

    bottomrow = finfo['ROW'] == plot.facet.nrow
    leftcol = finfo['COL'] == 1

    # Remove unwanted
    if isinstance(plot.facet, facet_wrap):
        if not finfo['AXIS_X']:
            ax.xaxis.set_ticks_position('none')
            ax.xaxis.set_ticklabels([])
        if not finfo['AXIS_Y']:
            ax.yaxis.set_ticks_position('none')
            ax.yaxis.set_ticklabels([])
        if finfo['AXIS_X']:
            ax.xaxis.set_ticks_position('bottom')
        if finfo['AXIS_Y']:
            ax.yaxis.set_ticks_position('left')
    else:
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


def add_labels_and_title(plot):
    fig = plot.figure
    xlabel = plot.labels.get('x', '')
    ylabel = plot.labels.get('y', '')
    title = plot.labels.get('title', '')

    d = dict(
        axis_title_x=fig.text(0.5, 0.08, xlabel,
                              ha='center', va='top'),
        axis_title_y=fig.text(0.09, 0.5, ylabel,
                              ha='right', va='center',
                              rotation='vertical'),
        plot_title=fig.text(0.5, 0.92, title,
                            ha='center', va='bottom'))

    fig._themeable.update(d)


# TODO Need to use theme (element_rect) for the colors
def draw_facet_label(plot, finfo, ax):
    """
    Draw facet label onto the axes.

    This function will only draw labels if they
    are needed.

    Parameters
    ----------
    plot : ggplot
        ggplot object
    finfo : dict-like
        facet information
    ax : axes
        current axes
    fig : Figure
        current figure
    """
    fcwrap = isinstance(plot.facet, facet_wrap)
    fcgrid = isinstance(plot.facet, facet_grid)
    toprow = finfo['ROW'] == 1
    rightcol = finfo['COL'] == plot.facet.ncol

    if not fcgrid and not fcwrap:
        return

    if fcgrid and not toprow and not rightcol:
        return

    # The facet labels are placed onto the figure using
    # transAxes dimensions. The line height and line
    # width are mapped to the same [0, 1] range
    # i.e (pts) * (inches / pts) * (1 / inches)
    # plus a padding factor of 1.6
    bbox = ax.get_window_extent().transformed(
        plot.figure.dpi_scale_trans.inverted())
    w, h = bbox.width, bbox.height  # in inches

    fs = float(plot.theme._rcParams['font.size'])

    # linewidth in transAxes
    lwy = fs / (72.27*h)
    lwx = fs / (72.27*w)

    # bbox height (along direction of text) of
    # labels in transAxes
    hy = 1.6 * lwy
    hx = 1.6 * lwx

    # text location in transAxes
    y = 1 + hy/2.4
    x = 1 + hx/2.4

    themeable = plot.figure._themeable
    for key in ('strip_text_x', 'strip_text_y',
                'strip_background_x', 'strip_background_y'):
        if key not in themeable:
            themeable[key] = []

    def draw_label(label, location):
        """
        Create a background patch and put a label on it
        """
        rotation = 90
        if location == 'right':
            _x, _y = x, 0.5
            xy = (1, 0)
            rotation = -90
            box_width = hx
            box_height = 1
        else:
            _x, _y = 0.5, y
            xy = (0, 1)
            rotation = 0
            box_width = 1
            box_height = hy

        rect = mpatch.FancyBboxPatch(xy,
                                     width=box_width,
                                     height=box_height,
                                     facecolor='lightgrey',
                                     edgecolor='None',
                                     linewidth=0,
                                     transform=ax.transAxes,
                                     zorder=1,
                                     boxstyle='square, pad=0',
                                     clip_on=False)

        text = mtext.Text(_x, _y, label,
                          transform=ax.transAxes,
                          rotation=rotation,
                          verticalalignment='center',
                          horizontalalignment='center',
                          zorder=1.2,  # higher than rect
                          clip_on=False)

        ax.add_artist(rect)
        ax.add_artist(text)

        if location == 'right':
            themeable['strip_background_y'].append(rect)
            themeable['strip_text_y'].append(text)
        else:
            themeable['strip_background_x'].append(rect)
            themeable['strip_text_x'].append(text)

    # facet_wrap #
    if fcwrap:
        label = finfo[plot.facet.vars[0]]
        draw_label(label, 'top')

    # facet_grid #
    if fcgrid and toprow and len(plot.facet.cols):
        label = finfo[plot.facet.cols[0]]
        draw_label(label, 'top')

    if fcgrid and rightcol and len(plot.facet.rows):
        label = finfo[plot.facet.rows[0]]
        draw_label(label, 'right')


def apply_facet_spacing(plot):
    # TODO: spaces should depend on the axis horizontal
    # and vertical lengths since the values are in
    # transAxes dimensions
    if isinstance(plot.facet, facet_wrap):
        plt.subplots_adjust(wspace=.05, hspace=.20)
    else:
        plt.subplots_adjust(wspace=.05, hspace=.05)

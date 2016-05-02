from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import sys
from copy import deepcopy

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnchoredOffsetbox
import matplotlib.text as mtext
import matplotlib.patches as mpatch
from patsy.eval import EvalEnvironment
from six.moves import zip

from .components.aes import aes, make_labels
from .components.panel import Panel
from .components.layer import Layers
from .facets import facet_null, facet_grid, facet_wrap
from .themes.theme import theme_get
from .utils.ggutils import gg_context, ggplot_options
from .utils.exceptions import GgplotError
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
    Create a new ggplot object

    Parameters
    ----------
    aesthetics :  aes
        Default aesthetics for the plot. These will be used
        by all layers unless specifically overridden.
    data :  dataframe
        Default data for for plot. Every layer that does not
        have data of its own will use this one.
    environment : namespace
        If an variable defined in the aesthetic mapping is not
        found in the data, ggplot will look for it in this
        namespace. It defaults to using the environment/namespace
        in which `ggplot()` is called.
    """

    def __init__(self, mapping=None, data=None, environment=None):
        # Allow some sloppiness
        if not isinstance(mapping, aes):
            mapping, data = data, mapping
        if mapping is None:
            mapping = aes()

        if (data is not None and
                not isinstance(data, pd.DataFrame)):
            raise GgplotError(
                'data must be a dataframe or None if each '
                'layer will have separate data.')

        self.data = data
        self.mapping = mapping
        self.facet = facet_null()
        self.labels = make_labels(mapping)
        self.layers = Layers()
        self.guides = guides()
        self.scales = Scales()
        self.theme = None
        self.coordinates = coord_cartesian()
        self.environment = environment or EvalEnvironment.capture(1)
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

        # don't make a deepcopy of data, or environment
        shallow = {'data', 'environment'}
        for key, item in self.__dict__.items():
            if key in shallow:
                result.__dict__[key] = self.__dict__[key]
            else:
                result.__dict__[key] = deepcopy(self.__dict__[key], memo)

        return result

    def _make_axes(self):
        """
        Create MPL figure and axes

        Note
        ----
        This method creates a grid of axes and
        unsed ones are turned off.
        A dict `figure._themeable` is attached to
        the figure to get a handle on objects that
        may be themed
        """
        if ggplot_options['close_all_figures']:
            plt.close("all")

        figure, axs = plt.subplots(self.facet.nrow,
                                   self.facet.ncol,
                                   sharex=False,
                                   sharey=False)

        # TODO: spaces should depend on the horizontal
        # and vertical lengths of the axes since the
        # spacing values are in transAxes dimensions
        if isinstance(self.facet, facet_wrap):
            hspace = len(self.facet.vars) * .20
            plt.subplots_adjust(wspace=.05, hspace=hspace)
        else:
            plt.subplots_adjust(wspace=.05, hspace=.05)

        figure._themeable = {}
        try:
            axs = axs.flatten()
        except AttributeError:
            axs = [axs]

        for ax in axs[len(self.panel.layout):]:
            ax.axis('off')
        axs = axs[:len(self.panel.layout)]

        self.theme.setup_figure(figure)
        self.axs = self.panel.axs = axs
        self.figure = self.theme.figure = figure

    def draw(self):
        """
        Render the complete plot and return the matplotlib figure
        """
        # Prevent against any modifications to the users
        # ggplot object. Do the copy here as we may/may not
        # assign a default theme
        self = deepcopy(self)
        self.build()

        # If no theme we use the default
        self.theme = self.theme or theme_get()

        with gg_context(theme=self.theme):
            self.draw_plot()
            self.draw_legend()
            add_labels_and_title(self)

            # Theming
            for ax in self.axs:
                self.theme.apply(ax)

            self.theme.apply_figure(self.figure)

        return self.figure

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
        self._make_axes()

        # Draw the geoms
        for layer in self.layers:
            layer.draw(self.panel, self.coordinates)

        # Decorate the axes
        #   - xaxis & yaxis breaks, labels, limits, ...
        #   - facet labels
        #
        # ploc is the panel location (left to right, top to bottom)
        for ploc, finfo in self.panel.layout.iterrows():
            panel_scales = self.panel.ranges[ploc]
            ax = self.panel.axs[ploc]
            set_breaks_and_labels(self, panel_scales, finfo, ax)
            draw_facet_label(self, finfo, ax)

    def build(self):
        """
        Build ggplot for rendering.

        Note
        ----
        This method modifies the ggplot object. The caller is responsible
        for making a copy and using that to make the method call.
        """
        plot = self

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

        # Each layer gets the final data used for plotting
        for layer, fdata in zip(layers, data):
            layer.final_data = fdata

    def draw_legend(self):
        legend_box = self.guides.build(self)
        if not legend_box:
            return

        position = self.theme._params['legend_position']

        # At what point (e.g [.94, .5]) on the figure
        # to place which point (e.g 6, for center left) of
        # the legend box
        _x = 0.92
        # Prevent overlap with the facet label
        if isinstance(self.facet, facet_grid):
            _x += .025 * len(self.facet.rows)
        lookup = {
            'right': (6, (_x, 0.5)),     # center left
            'left': (7, (0.07, 0.5)),    # center right
            'top': (8, (0.5, 0.92)),     # bottom center
            'bottom': (9, (0.5, 0.07))}  # upper center
        loc, box_to_anchor = lookup[position]
        anchored_box = AnchoredOffsetbox(
            loc=loc,
            child=legend_box,
            pad=0.,
            frameon=False,
            # Spacing goes here
            bbox_to_anchor=box_to_anchor,
            bbox_transform=self.figure.transFigure,
            borderpad=0.)

        self.figure._themeable['legend_background'] = anchored_box
        ax = self.axs[0]
        ax.add_artist(anchored_box)


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

    # breaks
    ax.set_xticks(ranges['x_major'])
    ax.set_yticks(ranges['y_major'])

    # minor breaks
    ax.set_xticks(ranges['x_minor'], minor=True)
    ax.set_yticks(ranges['y_minor'], minor=True)

    # labels
    ax.set_xticklabels(ranges['x_labels'])
    ax.set_yticklabels(ranges['y_labels'])

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
    # Get the axis labels (default or specified by user)
    # and let the coordinate modify them e.g. flip
    labels = plot.coordinates.labels(
        {'x': plot.labels.get('x', ''),
         'y': plot.labels.get('y', '')})
    title = plot.labels.get('title', '')
    center = 0.5

    # This is finicky. Should be changed when MPL
    # finally has a constraint based layout manager.
    xtitle_y = 0.08
    ytitle_x = 0.09
    title_y = 0.92
    if isinstance(plot.facet, facet_wrap):
        title_y += 0.025 * len(plot.facet.vars)
    elif isinstance(plot.facet, facet_grid):
        title_y += 0.04 * len(plot.facet.cols)

    d = dict(
        axis_title_x=fig.text(center, xtitle_y, labels['x'],
                              ha='center', va='top'),
        axis_title_y=fig.text(ytitle_x, center, labels['y'],
                              ha='right', va='center',
                              rotation='vertical'),
        plot_title=fig.text(center, title_y, title,
                            ha='center', va='bottom'))

    fig._themeable.update(d)


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
    pad = linespacing = 1.5
    lwy = (pad+fs) / (72.27*h)
    lwx = (pad+fs) / (72.27*w)

    themeable = plot.figure._themeable
    for key in ('strip_text_x', 'strip_text_y',
                'strip_background_x', 'strip_background_y'):
        if key not in themeable:
            themeable[key] = []

    def draw_label(label_info, location):
        """
        Create a background patch and put a label on it
        """
        num_lines = len(label_info)

        # bbox height (along direction of text) of
        # labels in transAxes
        hy = pad * lwy * num_lines
        hx = pad * lwx * num_lines

        # text location in transAxes
        y = 1 + hy/2.0
        x = 1 + hx/2.0

        if location == 'right':
            _x, _y = x, 0.5
            xy = (1, 0)
            rotation = -90
            box_width = hx
            box_height = 1
            label = '\n'.join(reversed(label_info))
        else:
            _x, _y = 0.5, y
            xy = (0, 1)
            rotation = 0
            box_width = 1
            box_height = hy
            label = '\n'.join(label_info)

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
                          linespacing=linespacing,
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

    # some meta information is added label information
    # to help out the labellers

    # facet_wrap #
    if fcwrap:
        label_info = finfo[list(plot.facet.vars)]
        label_info._meta = {'dimension': 'cols'}
        label_info = plot.facet.labeller(label_info)
        draw_label(label_info, 'top')

    # facet_grid #
    if fcgrid and toprow and len(plot.facet.cols):
        label_info = finfo[list(plot.facet.cols)]
        label_info._meta = {'dimension': 'cols'}
        label_info = plot.facet.labeller(label_info)
        draw_label(label_info, 'top')

    if fcgrid and rightcol and len(plot.facet.rows):
        label_info = finfo[list(plot.facet.rows)]
        label_info._meta = {'dimension': 'rows'}
        label_info = plot.facet.labeller(label_info)
        draw_label(label_info, 'right')

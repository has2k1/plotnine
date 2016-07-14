from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import sys
from copy import deepcopy

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnchoredOffsetbox
from patsy.eval import EvalEnvironment

from .aes import aes, make_labels
from .panel import Panel
from .layer import Layers
from .facets import facet_null, facet_grid, facet_wrap
from .themes.theme import theme_get
from .utils.ggutils import gg_context, gg_options, ggsave
from .utils.exceptions import GgplotError
from .scales.scales import Scales
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
        """
        Print/show the plot
        """
        self.draw()
        plt.show()
        return '<ggplot: (%d)>' % self.__hash__()

    def __deepcopy__(self, memo):
        """
        Deep copy without copying the dataframe and environment
        """
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        old = self.__dict__
        new = result.__dict__

        # don't make a deepcopy of data, or environment
        shallow = {'data', 'environment'}
        for key, item in old.items():
            if key in shallow:
                new[key] = old[key]
            else:
                new[key] = deepcopy(old[key], memo)

        return result

    def save(self, filename=None, **kwargs):
        """
        Save plot image

        Parameters
        ----------
        filename : str
            Filename
        kwargs : dict
            Arguments passed to :func:`~ggplot.ggutils.ggsave`
        """
        ggsave(filename=filename, plot=self, **kwargs)

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
            # Drawing
            self.draw_plot()
            self.draw_legend()
            self.draw_labels_and_title()
            # Theming
            self.theme.apply_axs(self.axs)
            self.theme.apply_figure(self.figure)

        return self.figure

    def draw_plot(self):
        """
        Draw the main plot(s) onto the axes.

        Return
        ------
        out : ggplot
            ggplot object with two new properties;
            ``axs`` and ``figure``.
        """
        # Good for development
        if gg_options['close_all_figures']:
            plt.close('all')

        # Create figure and axes
        figure, axs = self.facet.get_figure_and_axs(
            len(self.panel.layout))
        self.theme.setup_figure(figure)
        self.axs = self.panel.axs = axs
        self.figure = self.theme.figure = figure

        # Draw the geoms
        self.layers.draw(self.panel, self.coordinates)

        # Decorate the axes
        #   - xaxis & yaxis breaks, labels, limits, ...
        #   - facet labels
        #
        # pid is the panel location (left to right, top to bottom)
        for pid, layout_info in self.panel.layout.iterrows():
            panel_scales = self.panel.ranges[pid]
            ax = self.panel.axs[pid]
            self.facet.set_breaks_and_labels(panel_scales,
                                             layout_info, ax)
            self.facet.draw_label(layout_info, self.theme, ax)

    def build(self):
        """
        Build ggplot for rendering.

        Note
        ----
        This method modifies the ggplot object. The caller is
        responsible for making a copy and using that to make
        the method call.
        """
        if not self.layers:
            self += geom_blank()

        self.panel = Panel()
        layers = self.layers
        scales = self.scales
        panel = self.panel

        # Initialise panels, add extra data for margins & missing
        # facetting variables, and add on a PANEL variable to data
        panel.train_layout(layers, self)
        panel.map_layout(layers, self)

        # Compute aesthetics to produce data with generalised
        # variable names
        layers.compute_aesthetics(self)

        # Transform data using all scales
        layers.transform(scales)

        # Map and train positions so that statistics have access
        # to ranges and all positions are numeric
        panel.train_position(layers, scales.x, scales.y)
        panel.map_position(layers, scales.x, scales.y)

        # Apply and map statistics
        layers.compute_statistic(panel)
        layers.map_statistic(self)

        # Make sure missing (but required) aesthetics are added
        scales.add_missing(('x', 'y'))

        # Prepare data in geoms
        # e.g. from y and width to ymin and ymax
        layers.setup_data()

        # Apply position adjustments
        layers.compute_position(panel)

        # Reset position scales, then re-train and map.  This
        # ensures that facets have control over the range of
        # a plot.
        panel.reset_position_scales()
        panel.train_position(layers, scales.x, scales.y)
        panel.map_position(layers, scales.x, scales.y)

        # Train and map non-position scales
        npscales = scales.non_position_scales()
        if len(npscales):
            layers.train(npscales)
            layers.map(npscales)

        # Train coordinate system
        panel.train_ranges(self.coordinates)

        # fill in the defaults
        layers.use_defaults()

    def draw_legend(self):
        """
        Draw legend onto the figure
        """
        legend_box = self.guides.build(self)
        if not legend_box:
            return

        fig = self.figure
        left = fig.subplotpars.left
        right = fig.subplotpars.right
        top = fig.subplotpars.top
        bottom = fig.subplotpars.bottom
        width = fig.get_figwidth()
        height = fig.get_figheight()
        position = self.theme.params['legend_position']

        # The margin between the plot and legend is
        # a magic value(s) specified in inches, and
        # used to compute but the x, y location in
        # transFigure coordinates.
        if position == 'right':
            loc = 6
            x = right + 0.2/width
            y = 0.5
            if isinstance(self.facet, facet_grid):
                x += 0.25 * len(self.facet.rows)/width
        elif position == 'left':
            loc = 7
            x = left - 0.3/width
            y = 0.5
            if isinstance(self.facet, facet_grid):
                x -= 0.25 * len(self.facet.rows)/width
        elif position == 'top':
            loc = 8
            x = 0.5
            y = top + 0.6/height
            if isinstance(self.facet, facet_grid):
                y += 0.25 * len(self.facet.cols)/width
        elif position == 'bottom':
            loc = 9
            x = 0.5
            y = bottom - 0.6/height
        else:
            loc = 3
            x, y = position

        anchored_box = AnchoredOffsetbox(
            loc=loc,
            child=legend_box,
            pad=0.,
            frameon=False,
            bbox_to_anchor=(x, y),
            bbox_transform=self.figure.transFigure,
            borderpad=0.)

        anchored_box.set_zorder(90.1)
        self.figure._themeable['legend_background'] = anchored_box
        ax = self.axs[0]
        ax.add_artist(anchored_box)

    def draw_labels_and_title(self):
        """
        Draw labels and title onto the figure
        """
        fig = self.figure
        # Get the axis labels (default or specified by user)
        # and let the coordinate modify them e.g. flip
        labels = self.coordinates.labels(
            {'x': self.labels.get('x', ''),
             'y': self.labels.get('y', '')})
        title = self.labels.get('title', '')
        center = 0.5

        # This is finicky. Should be changed when MPL
        # finally has a constraint based layout manager.

        # Pick suitable values in inches and convert
        # theme to transFigure dimension. This gives
        # large spacing margins for oblong plots.
        left = fig.subplotpars.left
        top = fig.subplotpars.top
        bottom = fig.subplotpars.bottom
        width = fig.get_figwidth()
        height = fig.get_figheight()

        xtitle_y = bottom - 0.3/height
        ytitle_x = left - 0.3/width
        title_y = top + 0.1/height

        if isinstance(self.facet, facet_wrap):
            title_y += 0.25 * len(self.facet.vars)/height
        elif isinstance(self.facet, facet_grid):
            title_y += 0.25 * len(self.facet.cols)/height

        d = {
            'axis_title_x': fig.text(
                center, xtitle_y, labels['x'], ha='center', va='top'),
            'axis_title_y': fig.text(
                ytitle_x, center, labels['y'], ha='right',
                va='center', rotation='vertical'),
            'plot_title': fig.text(
                center, title_y, title, ha='center', va='bottom')
        }

        fig._themeable.update(d)

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import sys
from copy import deepcopy

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnchoredOffsetbox
import matplotlib.transforms as mtransforms
from patsy.eval import EvalEnvironment

from .aes import aes, make_labels
from .panel import Panel
from .layer import Layers
from .facets import facet_null
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
            Arguments passed to :func:`~ggplotx.ggutils.ggsave`
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
            self.draw_labels()
            self.draw_title()
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
        figure, axs = self.facet.make_figure_and_axs(
            self.panel, self.theme, self.coordinates)
        self.axs = self.panel.axs = axs
        self.figure = self.theme.figure = figure

        # Draw the geoms
        self.layers.draw(self.panel, self.coordinates)

        # Decorate the axes
        #   - xaxis & yaxis breaks, labels, limits, ...
        #   - facet labels
        #
        # pidx is the panel index (location left to right, top to bottom)
        for pidx, layout_info in self.panel.layout.iterrows():
            panel_scales = self.panel.ranges[pidx]
            self.facet.set_breaks_and_labels(
                panel_scales, layout_info, pidx)
            self.facet.draw_label(layout_info, pidx)

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

        figure = self.figure
        left = figure.subplotpars.left
        right = figure.subplotpars.right
        top = figure.subplotpars.top
        bottom = figure.subplotpars.bottom
        W, H = figure.get_size_inches()
        position = self.guides.position
        try:
            margin = self.theme.themeables.property('legend_margin')
        except KeyError:
            margin = 0.1
        right_strip_width = self.facet.strip_size('right')
        top_strip_height = self.facet.strip_size('top')

        # Other than when the legend is on the right the rest of
        # the computed x, y locations are not gauranteed not to
        # overlap with the axes or the labels. The user must then
        # use the legend_margin theme parameter to adjust the
        # location. This should get fixed when MPL has a better
        # layout manager.
        if position == 'right':
            loc = 6
            x = right + (right_strip_width+margin)/W
            y = 0.5
        elif position == 'left':
            loc = 7
            x = left - margin/W
            y = 0.5
        elif position == 'top':
            loc = 8
            x = 0.5
            y = top + (top_strip_height+margin)/H
        elif position == 'bottom':
            loc = 9
            x = 0.5
            y = bottom - margin/H
        else:
            loc = 10
            x, y = position

        anchored_box = AnchoredOffsetbox(
            loc=loc,
            child=legend_box,
            pad=0.,
            frameon=False,
            bbox_to_anchor=(x, y),
            bbox_transform=figure.transFigure,
            borderpad=0.)

        anchored_box.set_zorder(90.1)
        self.figure._themeable['legend_background'] = anchored_box
        ax = self.axs[0]
        ax.add_artist(anchored_box)

    def draw_labels(self):
        """
        Draw x and y labels onto the figure
        """
        # This is very laboured. Should be changed when MPL
        # finally has a constraint based layout manager.
        figure = self.figure
        get_property = self.theme.themeables.property

        try:
            xmargin = get_property('axis_title_margin_x')
        except KeyError:
            xmargin = 5

        try:
            ymargin = get_property('axis_title_margin_y')
        except KeyError:
            ymargin = 5

        # Get the axis labels (default or specified by user)
        # and let the coordinate modify them e.g. flip
        labels = self.coordinates.labels(
            {'x': self.labels.get('x', ''),
             'y': self.labels.get('y', '')})

        # The first axes object is on left, and the last axes object
        # is at the bottom. We change the transform so that the relevant
        # coordinate is in figure coordinates. This way we take
        # advantage of how MPL adjusts the label position so that they
        # do not overlap with the tick text. This works well for
        # facetting with scales='fixed' and also when not facetting.
        # first_ax = self.axs[0]
        # last_ax = self.axs[-1]

        xlabel = self.facet.last_ax.set_xlabel(
            labels['x'], labelpad=xmargin)
        ylabel = self.facet.first_ax.set_ylabel(
            labels['y'], labelpad=ymargin)

        xlabel.set_transform(mtransforms.blended_transform_factory(
            figure.transFigure, mtransforms.IdentityTransform()))
        ylabel.set_transform(mtransforms.blended_transform_factory(
            mtransforms.IdentityTransform(), figure.transFigure))

        figure._themeable['axis_title_x'] = xlabel
        figure._themeable['axis_title_y'] = ylabel

    def draw_title(self):
        """
        Draw title onto the figure
        """
        # This is very laboured. Should be changed when MPL
        # finally has a constraint based layout manager.
        figure = self.figure
        title = self.labels.get('title', '')
        get_property = self.theme.themeables.property

        # Pick suitable values in inches and convert them to
        # transFigure dimension. This gives fixed spacing
        # margins which work for oblong plots.
        top = figure.subplotpars.top
        W, H = figure.get_size_inches()

        # Adjust the title to avoid overlap with the facet
        # labels on the top row
        # 0.1/H is 0.1 inches in transFigure coordinates A fixed
        # margin value in inches prevents oblong plots from
        # getting unpredictably large spaces.
        try:
            fontsize = get_property('plot_title', 'size')
        except KeyError:
            fontsize = self.theme.rcParams.get('font.size', 12)

        try:
            linespacing = get_property('plot_title', 'linespacing')
        except KeyError:
            linespacing = 1.2

        line_size = fontsize / 72.27
        num_lines = len(title.split('\n'))
        title_size = line_size * linespacing * num_lines
        strip_height = self.facet.strip_size('top')

        x = 0.5
        y = top + (strip_height+title_size/2+0.1)/H

        text = figure.text(x, y, title, ha='center', va='center')
        figure._themeable['plot_title'] = text

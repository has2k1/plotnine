from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import os
import sys
from copy import copy, deepcopy
from warnings import warn

import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnchoredOffsetbox
import matplotlib.transforms as mtransforms
from patsy.eval import EvalEnvironment

from .aes import aes, make_labels
from .layer import Layers
from .facets import facet_null
from .facets.layout import Layout
from .options import get_option
from .themes.theme import theme, theme_get
from .utils import suppress, to_inches, from_inches
from .exceptions import PlotnineError
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
            raise PlotnineError(
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
        self.layout = None
        self.figure = None

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
                memo[id(new[key])] = new[key]
            else:
                new[key] = deepcopy(old[key], memo)

        return result

    def __iadd__(self, other):
        """
        Add other to ggplot object
        """
        try:
            return other.__radd__(self, inplace=True)
        except TypeError:
            return other.__radd__(self)

    def __rrshift__(self, other):
        """
        Overload the >> operator to receive a dataframe
        """
        if isinstance(other, pd.DataFrame):
            if self.data is None:
                self.data = other
            else:
                raise PlotnineError(
                    "`>>` failed, ggplot object has data.")
        else:
            msg = "Unknown type of data -- {!r}"
            raise TypeError(msg.format(type(other)))
        return self

    def draw(self):
        """
        Render the complete plot and return the matplotlib figure
        """
        # Prevent against any modifications to the users
        # ggplot object. Do the copy here as we may/may not
        # assign a default theme
        self = deepcopy(self)
        self._build()

        # If no theme we use the default
        self.theme = self.theme or theme_get()

        try:
            with mpl.rc_context():
                # rcparams theming
                self.theme.apply_rcparams()
                # Drawing
                self._draw_plot()
                self._draw_legend()
                self._draw_labels()
                self._draw_title()
                # Artist object theming
                self.theme.apply_axs(self.axs)
                self.theme.apply_figure(self.figure)
        except Exception as err:
            if self.figure is not None:
                plt.close(self.figure)
            raise err

        return self.figure

    def _draw_plot(self):
        """
        Draw the main plot(s) onto the axes.

        Return
        ------
        out : ggplot
            ggplot object with two new properties;
            ``axs`` and ``figure``.
        """
        # Good for development
        if get_option('close_all_figures'):
            plt.close('all')

        # Create figure and axes
        figure, axs = self.facet.make_figure_and_axs(
            self.layout, self.theme, self.coordinates)
        self.axs = self.layout.axs = axs
        self.figure = self.theme.figure = figure

        # Draw the geoms
        self.layers.draw(self.layout, self.coordinates)

        # Decorate the axes
        #   - xaxis & yaxis breaks, labels, limits, ...
        #   - facet labels
        #
        # pidx is the panel index (location left to right, top to bottom)
        for pidx, layout_info in self.layout.layout.iterrows():
            panel_params = self.layout.panel_params[pidx]
            self.facet.set_breaks_and_labels(
                panel_params, layout_info, pidx)
            self.facet.draw_label(layout_info, pidx)

    def _build(self):
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

        self.layout = Layout()
        layers = self.layers
        scales = self.scales
        layout = self.layout

        # Give each layer a copy of the data that it will need
        layers.generate_data(self.data)

        # Initialise panels, add extra data for margins & missing
        # facetting variables, and add on a PANEL variable to data
        layout.setup(layers, self)

        # Compute aesthetics to produce data with generalised
        # variable names
        layers.compute_aesthetics(self)

        # Transform data using all scales
        layers.transform(scales)

        # Map and train positions so that statistics have access
        # to ranges and all positions are numeric
        layout.train_position(layers, scales.x, scales.y)
        layout.map_position(layers)

        # Apply and map statistics
        layers.compute_statistic(layout)
        layers.map_statistic(self)

        # Make sure missing (but required) aesthetics are added
        scales.add_missing(('x', 'y'))

        # Prepare data in geoms
        # e.g. from y and width to ymin and ymax
        layers.setup_data()

        # Apply position adjustments
        layers.compute_position(layout)

        # Reset position scales, then re-train and map.  This
        # ensures that facets have control over the range of
        # a plot.
        layout.reset_position_scales()
        layout.train_position(layers, scales.x, scales.y)
        layout.map_position(layers)

        # Train and map non-position scales
        npscales = scales.non_position_scales()
        if len(npscales):
            layers.train(npscales)
            layers.map(npscales)

        # Train coordinate system
        layout.setup_panel_params(self.coordinates)

        # fill in the defaults
        layers.use_defaults()

        # Allow stats to modify the layer data
        layers.finish_statistics()

        # Allow layout to modify data before rendering
        layout.finish_data(layers)

    def _draw_legend(self):
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
        get_property = self.theme.themeables.property
        # defaults
        spacing = 0.1
        strip_margin_x = 0
        strip_margin_y = 0

        with suppress(KeyError):
            spacing = get_property('legend_box_spacing')
        with suppress(KeyError):
            strip_margin_x = get_property('strip_margin_x')
        with suppress(KeyError):
            strip_margin_y = get_property('strip_margin_y')

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
            pad = right_strip_width*(1+strip_margin_x) + spacing
            x = right + pad/W
            y = 0.5
        elif position == 'left':
            loc = 7
            x = left - spacing/W
            y = 0.5
        elif position == 'top':
            loc = 8
            x = 0.5
            pad = top_strip_height*(1+strip_margin_y) + spacing
            y = top + pad/H
        elif position == 'bottom':
            loc = 9
            x = 0.5
            y = bottom - spacing/H
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

    def _draw_labels(self):
        """
        Draw x and y labels onto the figure
        """
        # This is very laboured. Should be changed when MPL
        # finally has a constraint based layout manager.
        figure = self.figure
        get_property = self.theme.themeables.property

        try:
            margin = get_property('axis_title_x', 'margin')
        except KeyError:
            pad_x = 5
        else:
            pad_x = margin.get_as('t', 'pt')

        try:
            margin = get_property('axis_title_y', 'margin')
        except KeyError:
            pad_y = 5
        else:
            pad_y = margin.get_as('r', 'pt')

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
            labels['x'], labelpad=pad_x)
        ylabel = self.facet.first_ax.set_ylabel(
            labels['y'], labelpad=pad_y)

        xlabel.set_transform(mtransforms.blended_transform_factory(
            figure.transFigure, mtransforms.IdentityTransform()))
        ylabel.set_transform(mtransforms.blended_transform_factory(
            mtransforms.IdentityTransform(), figure.transFigure))

        figure._themeable['axis_title_x'] = xlabel
        figure._themeable['axis_title_y'] = ylabel

    def _draw_title(self):
        """
        Draw title onto the figure
        """
        # This is very laboured. Should be changed when MPL
        # finally has a constraint based layout manager.
        figure = self.figure
        title = self.labels.get('title', '')
        rcParams = self.theme.rcParams
        get_property = self.theme.themeables.property

        # Pick suitable values in inches and convert them to
        # transFigure dimension. This gives fixed spacing
        # margins which work for oblong plots.
        top = figure.subplotpars.top
        W, H = figure.get_size_inches()

        # Adjust the title to avoid overlap with the facet
        # labels on the top row
        # pad/H is inches in transFigure coordinates. A fixed
        # margin value in inches prevents oblong plots from
        # getting unpredictably large spaces.
        try:
            fontsize = get_property('plot_title', 'size')
        except KeyError:
            fontsize = float(rcParams.get('font.size', 12))

        try:
            linespacing = get_property('plot_title', 'linespacing')
        except KeyError:
            linespacing = 1.2

        try:
            margin = get_property('plot_title', 'margin')
        except KeyError:
            pad = 0.09
        else:
            pad = margin.get_as('b', 'in')

        try:
            strip_margin_x = get_property('strip_margin_x')
        except KeyError:
            strip_margin_x = 0

        line_size = fontsize / 72.27
        num_lines = len(title.split('\n'))
        title_size = line_size * linespacing * num_lines
        strip_height = self.facet.strip_size('top')
        # vertical adjustment
        strip_height *= (1 + strip_margin_x)

        x = 0.5
        y = top + (strip_height+title_size/2+pad)/H

        text = figure.text(x, y, title, ha='center', va='center')
        figure._themeable['plot_title'] = text

    def _save_filename(self, ext):
        """
        Default filename used by the save method

        Parameters
        ----------
        ext : str
            Extension e.g. png, pdf, ...
        """
        hash_token = abs(self.__hash__())
        return 'plotnine-save-{}.{}'.format(hash_token, ext)

    def save(self, filename=None, format=None, path=None,
             width=None, height=None, units='in',
             dpi=None, limitsize=True, **kwargs):
        """
        Save a ggplot object as an image file

        Parameters
        ----------
        filename : str or file
            File name or file to write the plot to.
        format : str
            Image format to use, automatically extract from
            file name extension.
        path : str
            Path to save plot to (if you just want to set path and
            not filename).
        width : number
            Width (defaults to the width of current plotting window).
        height : number
            Height (defaults to the height of current plotting window).
        units : str
            Units for width and height when either one is explicitly
            specified (in, cm, or mm).
        dpi : float
            DPI to use for raster graphics. If None, defaults to using
            the `dpi` of theme, if none is set then a `dpi` of 100.
        limitsize : bool
            If ``True`` (the default), ggsave will not save images
            larger than 50x50 inches, to prevent the common error
            of specifying dimensions in pixels.
        kwargs : dict
            Additional arguments to pass to matplotlib `savefig()`.
        """
        fig_kwargs = {'bbox_inches': 'tight',  # 'tight' is a good default
                      'format': format}
        fig_kwargs.update(kwargs)
        figure = [None]  # Python 3 a nonlocal

        # theme
        self.theme = self.theme or theme_get()

        # dpi
        if dpi is None:
            try:
                dpi = self.theme.themeables.property('dpi')
            except KeyError:
                dpi = 100
                # Do not modify original
                self.theme = copy(self.theme) + theme(dpi=dpi)

            # Should not need this with MPL 2.0
            fig_kwargs['dpi'] = dpi

        # filename
        print_filename = False
        if filename is None:
            ext = format if format else 'pdf'
            filename = self._save_filename(ext)
            print_filename = True

        if path:
            filename = os.path.join(path, filename)

        # Helper function so that we can clean up when it fails
        def _save():
            fig = figure[0] = self.draw()

            # savefig ignores the figure face & edge colors
            facecolor = fig.get_facecolor()
            edgecolor = fig.get_edgecolor()
            if edgecolor:
                fig_kwargs['facecolor'] = facecolor
            if edgecolor:
                fig_kwargs['edgecolor'] = edgecolor
                fig_kwargs['frameon'] = True

            _w, _h = fig.get_size_inches()
            print_size = width is None or height is None
            w = _w if width is None else to_inches(width, units)
            h = _h if height is None else to_inches(height, units)

            if print_size:
                warn("Saving {0} x {1} {2} image.".format(
                     from_inches(w, units),
                     from_inches(h, units), units))

            if print_filename:
                warn('Filename: {}'.format(filename))

            if limitsize and (w > 25 or h > 25):
                raise PlotnineError(
                       "Dimensions exceed 25 inches "
                       "(height and width are specified in inches/cm/mm, "
                       "not pixels). If you are sure you want these "
                       "dimensions, use 'limitsize=False'.")

            fig.set_size_inches(w, h)
            fig.savefig(filename, **fig_kwargs)

        try:
            _save()
        except Exception as err:
            figure[0] and plt.close(figure[0])
            raise err
        else:
            figure[0] and plt.close(figure[0])


def ggsave(plot, *arg, **kwargs):
    """
    Save a ggplot object as an image file

    Use :meth:`ggplot.save` instead
    """
    return plot.save(*arg, **kwargs)

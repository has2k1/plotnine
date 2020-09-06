# -*- coding: utf-8 -*-
import os
import sys
from copy import deepcopy
from contextlib import suppress
from types import SimpleNamespace as NS
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
from .utils import to_inches, from_inches, defaults, order_as_mapping_data
from .exceptions import PlotnineError, PlotnineWarning
from .scales.scales import Scales
from .coords import coord_cartesian
from .guides.guides import guides
from .geoms import geom_blank


# Show plots if in interactive mode
if sys.flags.interactive:
    plt.ion()


class ggplot:
    """
    Create a new ggplot object

    Parameters
    ----------
    aesthetics : aes
        Default aesthetics for the plot. These will be used
        by all layers unless specifically overridden.
    data :  dataframe
        Default data for for plot. Every layer that does not
        have data of its own will use this one.
    environment : dict, ~patsy.Eval.EvalEnvironment
        If a variable defined in the aesthetic mapping is not
        found in the data, ggplot will look for it in this
        namespace. It defaults to using the environment/namespace.
        in which `ggplot()` is called.
    """

    def __init__(self, mapping=None, data=None, environment=None):
        # Allow some sloppiness
        mapping, data = order_as_mapping_data(mapping, data)
        if mapping is None:
            mapping = aes()

        # Recognize plydata groups
        if hasattr(data, 'group_indices') and 'group' not in mapping:
            mapping = mapping.copy()
            mapping['group'] = data.group_indices()

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
        self.watermarks = []
        self.axs = None

    def __repr__(self):
        """
        Print/show the plot
        """
        # Do not draw if drawn already.
        # This prevents a needless error when reusing figure & axes
        # in the jupyter notebook.
        if not self.figure:
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
        shallow = {'data', 'environment', 'figure'}
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

    def __add__(self, other):
        """
        Add to ggitems from a list

        Parameters
        ----------
        other : object or list
            Either an object that knows how to "radd"
            itself to a ggplot, or a list of such objects.
        """
        if isinstance(other, list):
            self = deepcopy(self)
            for item in other:
                self += item
            return self
        else:
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

    def draw(self, return_ggplot=False):
        """
        Render the complete plot

        Parameters
        ----------
        return_ggplot : bool
            If ``True``, return ggplot object.

        Returns
        -------
        fig : ~matplotlib.figure.Figure
            Matplotlib figure
        plot : ggplot (optional)
            The ggplot object used for drawn, if ``return_ggplot`` is
            ``True``.

        Notes
        -----
        This method does not modify the original ggplot object. You can
        get the modified ggplot object with :py:`return_ggplot=True`.
        """
        # Pandas deprecated is_copy, and when we create new dataframes
        # from slices we do not want complaints. We always uses the
        # new frames knowing that they are separate from the original.
        with pd.option_context('mode.chained_assignment', None):
            return self._draw(return_ggplot)

    def _draw(self, return_ggplot=False):
        # Prevent against any modifications to the users
        # ggplot object. Do the copy here as we may/may not
        # assign a default theme
        self = deepcopy(self)
        self._build()

        # If no theme we use the default
        self.theme = self.theme or theme_get()

        try:
            with mpl.rc_context(self.theme.rcParams):
                # setup
                figure, axs = self._create_figure()
                self._setup_parameters()
                self._resize_panels()
                # Drawing
                self._draw_layers()
                self._draw_labels()
                self._draw_breaks_and_labels()
                self._draw_legend()
                self._draw_title()
                self._draw_watermarks()
                # Artist object theming
                self._apply_theme()  # !!
        except Exception as err:
            if self.figure is not None:
                plt.close(self.figure)
            raise err

        if return_ggplot:
            output = self.figure, self
        else:
            output = self.figure

        return output

    def _draw_using_figure(self, figure, axs):
        """
        Draw onto already created figure and axes

        This is can be used to draw animation frames,
        or inset plots. It is intended to be used
        after the key plot has been drawn.

        Parameters
        ----------
        figure : ~matplotlib.figure.Figure
            Matplotlib figure
        axs : array_like
            Array of Axes onto which to draw the plots
        """
        self = deepcopy(self)
        self._build()

        self.theme = self.theme or theme_get()
        self.figure = figure
        self.axs = axs

        try:
            with mpl.rc_context(self.theme.rcParams):
                self._setup_parameters()
                self._draw_layers()
                self._draw_breaks_and_labels()
                self._draw_legend()
                self._apply_theme()
        except Exception as err:
            if self.figure is not None:
                plt.close(self.figure)
            raise err

        return self

    def _build(self):
        """
        Build ggplot for rendering.

        Notes
        -----
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

        # Update the label information for the plot
        layers.update_labels(self)

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

    def _setup_parameters(self):
        """
        Set facet properties
        """
        # facet
        self.facet.set(
            layout=self.layout,
            theme=self.theme,
            coordinates=self.coordinates,
            figure=self.figure,
            axs=self.axs
        )

        # layout
        self.layout.axs = self.axs
        # theme
        self.theme.figure = self.figure

    def _create_figure(self):
        """
        Create Matplotlib figure and axes
        """
        # Good for development
        if get_option('close_all_figures'):
            plt.close('all')

        figure = plt.figure()
        axs = self.facet.make_axes(
            figure,
            self.layout.layout,
            self.coordinates)

        # Dictionary to collect matplotlib objects that will
        # be targeted for theming by the themeables
        figure._themeable = {}

        self.figure = figure
        self.axs = axs
        return figure, axs

    def _resize_panels(self):
        """
        Resize panels
        """
        self.theme.setup_figure(self.figure)
        self.facet.spaceout_and_resize_panels()

    def _draw_layers(self):
        """
        Draw the main plot(s) onto the axes.
        """
        # Draw the geoms
        self.layers.draw(self.layout, self.coordinates)

    def _draw_breaks_and_labels(self):
        """
        Draw breaks and labels
        """
        # Decorate the axes
        #   - xaxis & yaxis breaks, labels, limits, ...
        #   - facet labels a.k.a strip text
        #
        # pidx is the panel index (location left to right, top to bottom)
        for pidx, layout_info in self.layout.layout.iterrows():
            ax = self.axs[pidx]
            panel_params = self.layout.panel_params[pidx]
            self.facet.draw_label(layout_info, ax)
            self.facet.set_limits_breaks_and_labels(panel_params, ax)

            # Remove unnecessary ticks and labels
            if not layout_info['AXIS_X']:
                ax.xaxis.set_tick_params(
                    which='both', bottom=False, labelbottom=False)
            if not layout_info['AXIS_Y']:
                ax.yaxis.set_tick_params(
                    which='both', left=False, labelleft=False)

            if layout_info['AXIS_X']:
                ax.xaxis.set_tick_params(which='both', bottom=True)
            if layout_info['AXIS_Y']:
                ax.yaxis.set_tick_params(which='both', left=True)

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
        labels = self.coordinates.labels(NS(
            x=self.layout.xlabel(self.labels),
            y=self.layout.ylabel(self.labels)
        ))
        # The first axes object is on left, and the last axes object
        # is at the bottom. We change the transform so that the relevant
        # coordinate is in figure coordinates. This way we take
        # advantage of how MPL adjusts the label position so that they
        # do not overlap with the tick text. This works well for
        # facetting with scales='fixed' and also when not facetting.
        # first_ax = self.axs[0]
        # last_ax = self.axs[-1]

        xlabel = self.facet.last_ax.set_xlabel(
            labels.x, labelpad=pad_x)
        ylabel = self.facet.first_ax.set_ylabel(
            labels.y, labelpad=pad_y)

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

    def _draw_watermarks(self):
        """
        Draw watermark onto figure
        """
        for wm in self.watermarks:
            wm.draw(self.figure)

    def _apply_theme(self):
        """
        Apply theme attributes to Matplotlib objects
        """
        self.theme.apply_axs(self.axs)
        self.theme.apply_figure(self.figure)

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

    def _update_labels(self, layer):
        """
        Update label data for the ggplot

        Parameters
        ----------
        layer : layer
            New layer that has just been added to the ggplot
            object.
        """
        mapping = make_labels(layer.mapping)
        default = make_labels(layer.stat.DEFAULT_AES)
        new_labels = defaults(mapping, default)
        self.labels = defaults(self.labels, new_labels)

    def save(self, filename=None, format=None, path=None,
             width=None, height=None, units='in',
             dpi=None, limitsize=True, verbose=True, **kwargs):
        """
        Save a ggplot object as an image file

        Parameters
        ----------
        filename : str, optional
            File name to write the plot to. If not specified, a name
            like “plotnine-save-<hash>.<format>” is used.
        format : str
            Image format to use, automatically extract from
            file name extension.
        path : str
            Path to save plot to (if you just want to set path and
            not filename).
        width : number, optional
            Width (defaults to value set by the theme). If specified
            the `height` must also be given.
        height : number, optional
            Height (defaults to value set by the theme). If specified
            the `width` must also be given.
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
        verbose : bool
            If ``True``, print the saving information.
        kwargs : dict
            Additional arguments to pass to matplotlib `savefig()`.
        """
        fig_kwargs = {'bbox_inches': 'tight',  # 'tight' is a good default
                      'format': format}
        fig_kwargs.update(kwargs)

        figure = [None]  # nonlocal

        # filename, depends on the object
        if filename is None:
            ext = format if format else 'pdf'
            filename = self._save_filename(ext)

        if path:
            filename = os.path.join(path, filename)

        # Preserve the users object
        self = deepcopy(self)

        # theme
        self.theme = self.theme or theme_get()

        # The figure size should be known by the theme
        if width is not None and height is not None:
            width = to_inches(width, units)
            height = to_inches(height, units)
            self += theme(figure_size=(width, height))
        elif (width is None and height is not None or
              width is not None and height is None):
            raise PlotnineError(
                "You must specify both width and height")

        width, height = self.theme.themeables.property('figure_size')

        if limitsize and (width > 25 or height > 25):
            raise PlotnineError(
                "Dimensions (width={}, height={}) exceed 25 inches "
                "(height and width are specified in inches/cm/mm, "
                "not pixels). If you are sure you want these "
                "dimensions, use 'limitsize=False'.".format(width, height))

        if dpi is None:
            try:
                self.theme.themeables.property('dpi')
            except KeyError:
                self.theme = self.theme + theme(dpi=100)
        else:
            self.theme = self.theme + theme(dpi=dpi)

        if verbose:
            warn("Saving {0} x {1} {2} image.".format(
                 from_inches(width, units),
                 from_inches(height, units), units), PlotnineWarning)
            warn('Filename: {}'.format(filename), PlotnineWarning)

        # Helper function so that we can clean up when it fails
        def _save():
            fig = figure[0] = self.draw()

            # savefig ignores the figure face & edge colors
            facecolor = fig.get_facecolor()
            edgecolor = fig.get_edgecolor()
            if facecolor:
                fig_kwargs['facecolor'] = facecolor
            if edgecolor:
                fig_kwargs['edgecolor'] = edgecolor

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


def save_as_pdf_pages(plots, filename=None, path=None, verbose=True, **kwargs):
    """
    Save multiple :class:`ggplot` objects to a PDF file, one per page.

    Parameters
    ----------
    plots : collection or generator of :class:`ggplot`
        Plot objects to write to file. `plots` may be either a
        collection such as a :py:class:`list` or :py:class:`set`:

        >>> base_plot = ggplot(…)
        >>> plots = [base_plot + ggtitle('%d of 3' % i) for i in range(1, 3)]
        >>> save_as_pdf_pages(plots)

        or, a generator that yields :class:`ggplot` objects:

        >>> def myplots():
        >>>     for i in range(1, 3):
        >>>         yield ggplot(…) + ggtitle('%d of 3' % i)
        >>> save_as_pdf_pages(myplots())

    filename : :py:class:`str`, optional
        File name to write the plot to. If not specified, a name
        like “plotnine-save-<hash>.pdf” is used.
    path : :py:class:`str`, optional
        Path to save plot to (if you just want to set path and
        not filename).
    verbose : :py:class:`bool`
        If ``True``, print the saving information.
    kwargs : :py:class:`dict`
        Additional arguments to pass to
        :py:meth:`matplotlib.figure.Figure.savefig`.

    Notes
    -----
    Using pandas' :meth:`~pandas.DataFrame.groupby` methods, tidy data
    can be “faceted” across pages:

    >>> from plotnine.data import mtcars
    >>> def facet_pages(column)
    >>>     base_plot = [
    >>>         aes(x='wt', y='mpg', label='name'),
    >>>         geom_text(),
    >>>         ]
    >>>     for label, group_data in mtcars.groupby(column):
    >>>         yield ggplot(group_data) + base_plot + ggtitle(label)
    >>> save_as_pdf_pages(facet_pages('cyl'))

    Unlike :meth:`ggplot.save`, :meth:`save_as_pdf_pages` does not
    process arguments for `height` or `width`. To set the figure size,
    add :class:`~plotnine.themes.themeable.figure_size` to the theme
    for some or all of the objects in `plots`:

    >>> plot = ggplot(…)
    >>> # The following are equivalent
    >>> plot.save('filename.pdf', height=6, width=8)
    >>> save_as_pdf_pages([plot + theme(figure_size=(8, 6))])
    """
    from itertools import chain

    from matplotlib.backends.backend_pdf import PdfPages

    # as in ggplot.save()
    fig_kwargs = {'bbox_inches': 'tight'}
    fig_kwargs.update(kwargs)

    figure = [None]

    # If plots is already an iterator, this is a no-op; otherwise convert a
    # list, etc. to an iterator
    plots = iter(plots)
    peek = []

    # filename, depends on the object
    if filename is None:
        # Take the first element from the iterator, store it, and use it to
        # generate a file name
        peek = [next(plots)]
        filename = peek[0]._save_filename('pdf')

    if path:
        filename = os.path.join(path, filename)

    if verbose:
        warn('Filename: {}'.format(filename), PlotnineWarning)

    with PdfPages(filename) as pdf:
        # Re-add the first element to the iterator, if it was removed
        for plot in chain(peek, plots):
            try:
                fig = figure[0] = plot.draw()

                # as in ggplot.save()
                facecolor = fig.get_facecolor()
                edgecolor = fig.get_edgecolor()
                if facecolor:
                    fig_kwargs['facecolor'] = facecolor
                if edgecolor:
                    fig_kwargs['edgecolor'] = edgecolor

                # Save as a page in the PDF file
                pdf.savefig(figure[0], **fig_kwargs)
            except AttributeError as err:
                msg = 'non-ggplot object of %s: %s' % (type(plot), plot)
                raise TypeError(msg) from err
            except Exception:
                raise
            finally:
                # Close the figure whether or not there was an exception, to
                # conserve memory when plotting a large number of pages
                figure[0] and plt.close(figure[0])

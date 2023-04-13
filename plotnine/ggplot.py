from __future__ import annotations

import typing
from collections.abc import Sequence
from copy import deepcopy
from itertools import chain
from pathlib import Path
from types import SimpleNamespace as NS
from typing import Any, Dict, Iterable, Optional, Union
from warnings import warn

import pandas as pd

from .coords import coord_cartesian
from .exceptions import PlotnineError, PlotnineWarning
from .facets import facet_null
from .facets.layout import Layout
from .geoms.geom_blank import geom_blank
from .guides.guides import guides
from .iapi import mpl_save_view
from .layer import Layers
from .mapping.aes import aes, make_labels
from .options import SUBPLOTS_ADJUST, get_option
from .scales.scales import Scales
from .themes.theme import theme, theme_get
from .utils import (
    from_inches,
    is_data_like,
    order_as_data_mapping,
    to_inches,
    ungroup,
)

if typing.TYPE_CHECKING:
    from plotnine.typing import (
        Axes,
        Coord,
        DataLike,
        EvalEnvironment,
        Facet,
        Figure,
        Layer,
        PlotAddable,
        Theme,
        Watermark,
    )


class ggplot:
    """
    Create a new ggplot object

    Parameters
    ----------
    data : dataframe
        Default data for plot. Every layer that does not
        have data of its own will use this one.
    mapping : aes
        Default aesthetics mapping for the plot. These will be used
        by all layers unless specifically overridden.
    environment : ~patsy.Eval.EvalEnvironment
        If a variable defined in the aesthetic mapping is not
        found in the data, ggplot will look for it in this
        namespace. It defaults to using the environment/namespace.
        in which `ggplot()` is called.
    """

    figure: Figure
    axs: list[Axes]
    theme: Theme
    facet: Facet
    coordinates: Coord

    def __init__(
        self,
        data: DataLike | None = None,
        mapping: aes | None = None,
        environment: EvalEnvironment | None = None,
    ):
        from patsy.eval import EvalEnvironment

        # Allow some sloppiness
        data, mapping = order_as_data_mapping(data, mapping)
        self.data = data
        self.mapping = mapping if mapping is not None else aes()
        self.facet = facet_null()
        self.labels = make_labels(self.mapping)
        self.layers = Layers()
        self.guides = guides()
        self.scales = Scales()
        self.theme = theme_get()
        self.coordinates: Coord = coord_cartesian()
        self.environment = environment or EvalEnvironment.capture(1)
        self.layout = Layout()
        self.watermarks: list[Watermark] = []

        # build artefacts
        self._build_objs = NS()

    def __str__(self) -> str:
        """
        Print/show the plot
        """
        self.draw(show=True)

        # Return and empty string so that print(p) is "pretty"
        return ""

    def __repr__(self) -> str:
        """
        Print/show the plot
        """
        self.__str__()
        return "<ggplot: (%d)>" % self.__hash__()

    def __deepcopy__(self, memo: dict[Any, Any]) -> ggplot:
        """
        Deep copy without copying the dataframe and environment
        """
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        old = self.__dict__
        new = result.__dict__

        # don't make a deepcopy of data, or environment
        shallow = {"data", "environment", "figure", "_build_objs"}
        for key, item in old.items():
            if key in shallow:
                new[key] = old[key]
                memo[id(new[key])] = new[key]
            else:
                new[key] = deepcopy(old[key], memo)

        return result

    def __iadd__(
        self, other: PlotAddable | list[PlotAddable] | None
    ) -> ggplot:
        """
        Add other to ggplot object

        Parameters
        ----------
        other : object or Sequence
            Either an object that knows how to "radd"
            itself to a ggplot, or a list of such objects.
        """
        if isinstance(other, Sequence):
            for item in other:
                item.__radd__(self)
            return self
        elif other is None:
            return self
        else:
            return other.__radd__(self)

    def __add__(self, other: PlotAddable | list[PlotAddable] | None) -> ggplot:
        """
        Add to ggplot from a list

        Parameters
        ----------
        other : object or Sequence
            Either an object that knows how to "radd"
            itself to a ggplot, or a list of such objects.
        """
        self = deepcopy(self)
        return self.__iadd__(other)

    def __rrshift__(self, other: DataLike) -> ggplot:
        """
        Overload the >> operator to receive a dataframe
        """
        other = ungroup(other)
        if is_data_like(other):
            if self.data is None:
                self.data = other
            else:
                raise PlotnineError("`>>` failed, ggplot object has data.")
        else:
            msg = "Unknown type of data -- {!r}"
            raise TypeError(msg.format(type(other)))
        return self

    def draw(self, show: bool = False) -> Figure:
        """
        Render the complete plot

        Parameters
        ----------
        show : bool (default: False)
            Whether to show the plot.

        Returns
        -------
        fig : ~matplotlib.figure.Figure
            Matplotlib figure
        """
        # Do not draw if drawn already.
        # This prevents a needless error when reusing
        # figure & axes in the jupyter notebook.
        if hasattr(self, "figure"):
            return self.figure

        # Prevent against any modifications to the users
        # ggplot object. Do the copy here as we may/may not
        # assign a default theme
        self = deepcopy(self)
        with plot_context(self, show=show):
            self._build()

            # setup
            figure, axs = self._create_figure()
            self._setup_parameters()
            self.facet.strips.generate()
            self._resize_panels()

            # Drawing
            self._draw_layers()
            self._draw_labels()
            self._draw_breaks_and_labels()
            self._draw_legend()
            self._draw_title()
            self._draw_caption()
            self._draw_watermarks()

            # Artist object theming
            self.theme.apply()

        return self.figure

    def _draw_using_figure(self, figure: Figure, axs: list[Axes]) -> ggplot:
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
        self.figure = figure
        self.axs = axs
        with plot_context(self):
            self._build()
            self._setup_parameters()
            self.facet.strips.generate()
            self._draw_layers()
            self._draw_breaks_and_labels()
            self._draw_legend()
            self.theme.apply()

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

        layers = self._build_objs.layers = self.layers
        scales = self._build_objs.scales = self.scales
        layout = self._build_objs.layout = self.layout

        # Update the label information for the plot
        layers.update_labels(self)

        # Give each layer a copy of the data, the mappings and
        # the execution environment
        layers.setup(self)

        # Initialise panels, add extra data for margins & missing
        # facetting variables, and add on a PANEL variable to data
        layout.setup(layers, self)

        # Compute aesthetics to produce data with generalised
        # variable names
        layers.compute_aesthetics(self)

        # Transform data using all scales
        layers.transform(scales)

        # Make sure missing (but required) aesthetics are added
        scales.add_missing(("x", "y"))

        # Map and train positions so that statistics have access
        # to ranges and all positions are numeric
        layout.train_position(layers, scales)
        layout.map_position(layers)

        # Apply and map statistics
        layers.compute_statistic(layout)
        layers.map_statistic(self)

        # Prepare data in geoms
        # e.g. from y and width to ymin and ymax
        layers.setup_data()

        # Apply position adjustments
        layers.compute_position(layout)

        # Reset position scales, then re-train and map.  This
        # ensures that facets have control over the range of
        # a plot.
        layout.reset_position_scales()
        layout.train_position(layers, scales)
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
        self.facet.set_properties(self)
        # layout
        self.layout.axs = self.axs
        # theme
        self.theme.figure = self.figure
        self.theme.axs = self.axs

    def _create_figure(self) -> tuple[Figure, list[Axes]]:
        """
        Create Matplotlib figure and axes
        """
        import matplotlib.pyplot as plt

        # Good for development
        if get_option("close_all_figures"):
            plt.close("all")

        figure: Figure = plt.figure()  # pyright: ignore
        axs = self.facet.make_axes(
            figure, self.layout.layout, self.coordinates
        )

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
        # 1. Draw facet labels a.k.a strip text
        # 2. Decorate the axes
        #      - xaxis & yaxis breaks, labels, limits, ...
        #
        # pidx is the panel index (location left to right, top to bottom)
        self.facet.strips.draw()
        for layout_info in self.layout.get_details():
            pidx = layout_info.panel_index
            ax = self.axs[pidx]
            panel_params = self.layout.panel_params[pidx]
            self.facet.set_limits_breaks_and_labels(panel_params, ax)

            # Remove unnecessary ticks and labels
            if not layout_info.axis_x:
                ax.xaxis.set_tick_params(
                    which="both", bottom=False, labelbottom=False
                )
            if not layout_info.axis_y:
                ax.yaxis.set_tick_params(
                    which="both", left=False, labelleft=False
                )

            if layout_info.axis_x:
                ax.xaxis.set_tick_params(which="both", bottom=True)
            if layout_info.axis_y:
                ax.yaxis.set_tick_params(which="both", left=True)

    def _draw_legend(self):
        """
        Draw legend onto the figure
        """
        from matplotlib.offsetbox import AnchoredOffsetbox

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
        _property = self.theme.themeables.property
        spacing = _property("legend_box_spacing")
        strip_margin_x = _property("strip_margin_x")
        strip_margin_y = _property("strip_margin_y")

        right_strip_width = self.facet.strips.breadth("right")
        top_strip_height = self.facet.strips.breadth("top")

        # Other than when the legend is on the right the rest of
        # the computed x, y locations are not gauranteed not to
        # overlap with the axes or the labels. The user must then
        # use the legend_margin theme parameter to adjust the
        # location. This should get fixed when MPL has a better
        # layout manager.
        if position == "right":
            loc = "center left"
            pad = right_strip_width * (1 + strip_margin_x) + spacing
            x = right + pad / W
            y = 0.5
        elif position == "left":
            loc = "center right"
            x = left - spacing / W
            y = 0.5
        elif position == "top":
            loc = "lower center"
            x = 0.5
            pad = top_strip_height * (1 + strip_margin_y) + spacing
            y = top + pad / H
        elif position == "bottom":
            loc = "upper center"
            x = 0.5
            y = bottom - spacing / H
        else:
            loc = "center"
            x, y = position

        anchored_box = AnchoredOffsetbox(
            loc=loc,
            child=legend_box,
            pad=0.0,
            frameon=False,
            bbox_to_anchor=(x, y),
            bbox_transform=figure.transFigure,
            borderpad=0.0,
        )

        anchored_box.set_zorder(90.1)
        self.theme._targets["legend_background"] = anchored_box
        ax = self.axs[0]
        ax.add_artist(anchored_box)

    def _draw_labels(self):
        """
        Draw x and y labels onto the figure
        """
        from matplotlib.transforms import (
            IdentityTransform,
            blended_transform_factory,
        )

        # This is very laboured. Should be changed when MPL
        # finally has a constraint based layout manager.
        figure = self.figure
        theme = self.theme
        _property = self.theme.themeables.property

        pad_x = _property("axis_title_x", "margin").get_as("t", "pt")
        pad_y = _property("axis_title_y", "margin").get_as("r", "pt")

        # Get the axis labels (default or specified by user)
        # and let the coordinate modify them e.g. flip
        labels = self.coordinates.labels(
            self.layout.set_xy_labels(self.labels)
        )
        # The first axes object is on left, and the last axes object
        # is at the bottom. We change the transform so that the relevant
        # coordinate is in figure coordinates. This way we take
        # advantage of how MPL adjusts the label position so that they
        # do not overlap with the tick text. This works well for
        # facetting with scales='fixed' and also when not facetting.
        # first_ax = self.axs[0]
        # last_ax = self.axs[-1]

        xlabel = self.facet.last_ax.set_xlabel(labels.x, labelpad=pad_x)
        ylabel = self.facet.first_ax.set_ylabel(labels.y, labelpad=pad_y)

        xlabel.set_transform(
            blended_transform_factory(figure.transFigure, IdentityTransform())
        )
        ylabel.set_transform(
            blended_transform_factory(IdentityTransform(), figure.transFigure)
        )

        theme._targets["axis_title_x"] = xlabel
        theme._targets["axis_title_y"] = ylabel

    def _draw_title(self):
        """
        Draw title onto the figure
        """
        # This is very laboured. Should be changed when MPL
        # finally has a constraint based layout manager.
        figure = self.figure
        theme = self.theme
        title = self.labels.get("title", "")
        _property = self.theme.themeables.property

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

        linespacing = _property("plot_title", "linespacing")
        fontsize = _property("plot_title", "size")
        pad = _property("plot_title", "margin").get_as("b", "in")
        ha = _property("plot_title", "ha")
        strip_margin_y = _property("strip_margin_y")

        dpi = 72.27
        line_size = fontsize / dpi
        num_lines = len(title.split("\n"))
        title_size = line_size * linespacing * num_lines
        strip_height = self.facet.strips.breadth("top")
        strip_height *= 1 + strip_margin_y

        if ha == "left":
            x = SUBPLOTS_ADJUST["left"]
        elif ha == "right":
            x = SUBPLOTS_ADJUST["right"]
        else:
            # ha='center' is default
            x = 0.5

        y = top + (strip_height + title_size / 2 + pad) / H

        text = figure.text(x, y, title, ha=ha, va="center")
        theme._targets["plot_title"] = text

    def _draw_caption(self):
        """
        Draw caption onto the figure
        """
        # This is very laboured. Should be changed when MPL
        # finally has a constraint based layout manager.
        figure = self.figure
        theme = self.theme
        caption = self.labels.get("caption", "")
        _property = self.theme.themeables.property

        # Pick suitable values in inches and convert them to
        # transFigure dimension. This gives fixed spacing
        # margins which work for oblong plots.
        right = figure.subplotpars.right
        W, H = figure.get_size_inches()

        margin = _property("plot_caption", "margin")
        right_pad = margin.get_as("r", "in")
        top_pad = margin.get_as("t", "in")

        x = right - right_pad / W
        y = 0 - top_pad / H

        text = figure.text(x, y, caption, ha="right", va="top")
        theme._targets["plot_caption"] = text

    def _draw_watermarks(self):
        """
        Draw watermark onto figure
        """
        for wm in self.watermarks:
            wm.draw(self.figure)

    def _save_filename(self, ext: str) -> Path:
        """
        Make a filename for use by the save method

        Parameters
        ----------
        ext : str
            Extension e.g. png, pdf, ...
        """
        hash_token = abs(self.__hash__())
        return Path(f"plotnine-save-{hash_token}.{ext}")

    def _update_labels(self, layer: Layer):
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
        mapping.add_defaults(default)
        self.labels.add_defaults(mapping)

    def save_helper(
        self: ggplot,
        filename: Optional[Union[str, Path]] = None,
        format: Optional[str] = None,
        path: Optional[str] = None,
        width: Optional[float] = None,
        height: Optional[float] = None,
        units: str = "in",
        dpi: Optional[float] = None,
        limitsize: bool = True,
        verbose: bool = True,
        **kwargs: Any,
    ) -> mpl_save_view:
        """
        Create MPL figure that will be saved

        Notes
        -----
        This method has the same arguments as :meth:`ggplot.save`.
        Use it to get access to the figure that will be saved.
        """
        fig_kwargs: Dict[str, Any] = {
            "format": format,
        }
        fig_kwargs.update(kwargs)

        # filename, depends on the object
        if filename is None:
            ext = format if format else "pdf"
            filename = self._save_filename(ext)

        if path:
            filename = Path(path) / filename

        fig_kwargs["fname"] = filename

        # Preserve the users object
        self = deepcopy(self)

        # The figure size should be known by the theme
        if width is not None and height is not None:
            width = to_inches(width, units)
            height = to_inches(height, units)
            self += theme(figure_size=(width, height))
        elif (
            width is None
            and height is not None
            or width is not None
            and height is None
        ):
            raise PlotnineError("You must specify both width and height")

        width, height = self.theme.themeables.property("figure_size")
        assert width is not None
        assert height is not None

        if limitsize and (width > 25 or height > 25):
            raise PlotnineError(
                f"Dimensions ({width=}, {height=}) exceed 25 inches "
                "(height and width are specified in inches/cm/mm, "
                "not pixels). If you are sure you want these "
                "dimensions, use 'limitsize=False'."
            )

        if verbose:
            _w = from_inches(width, units)
            _h = from_inches(height, units)
            warn(f"Saving {_w} x {_h} {units} image.", PlotnineWarning)
            warn(f"Filename: {filename}", PlotnineWarning)

        if dpi is not None:
            self.theme = self.theme + theme(dpi=dpi)

        figure = self.draw(show=False)
        return mpl_save_view(figure, fig_kwargs)

    def save(
        self,
        filename: Union[str, Path] | None = None,
        format: str | None = None,
        path: str = "",
        width: float | None = None,
        height: float | None = None,
        units: str = "in",
        dpi: float | None = None,
        limitsize: bool = True,
        verbose: bool = True,
        **kwargs: Any,
    ):
        """
        Save a ggplot object as an image file

        Parameters
        ----------
        filename : str | pathlib.Path, optional
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
        sv = self.save_helper(
            filename=filename,
            format=format,
            path=path,
            width=width,
            height=height,
            units=units,
            dpi=dpi,
            limitsize=limitsize,
            verbose=verbose,
            **kwargs,
        )
        sv.figure.tight_layout()
        sv.figure.savefig(**sv.kwargs)


ggsave = ggplot.save


def save_as_pdf_pages(
    plots: Iterable[ggplot],
    filename: Optional[str | Path] = None,
    path: str | None = None,
    verbose: bool = True,
    **kwargs: Any,
):
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
    from matplotlib.backends.backend_pdf import PdfPages

    # as in ggplot.save()
    fig_kwargs = {"bbox_inches": "tight"}
    fig_kwargs.update(kwargs)

    # If plots is already an iterator, this is a no-op; otherwise
    # convert a list, etc. to an iterator
    plots = iter(plots)

    # filename, depends on the object
    if filename is None:
        # Take the first element from the iterator, store it, and
        # use it to generate a file name
        peek = [next(plots)]
        plots = chain(peek, plots)
        filename = peek[0]._save_filename("pdf")

    if path:
        filename = Path(path) / filename

    if verbose:
        warn(f"Filename: {filename}", PlotnineWarning)

    with PdfPages(filename) as pdf:
        # Re-add the first element to the iterator, if it was removed
        for plot in plots:
            fig = plot.draw()
            # Save as a page in the PDF file
            pdf.savefig(fig, **fig_kwargs)


class plot_context:
    """
    Context to setup the environment within with the plot is built

    Parameters
    ----------
    plot : ggplot
        ggplot object to be built within the context.
    show : bool (default: False)
        Whether to show (``plt.show()``) the plot before the context
        exits.
    """

    def __init__(self, plot: ggplot, show: bool = False):
        self.plot = plot
        self.show = show

    def __enter__(self) -> plot_context:
        """
        Enclose in matplolib & pandas environments
        """
        import matplotlib as mpl

        self.plot.theme._targets = {}
        self.rc_context = mpl.rc_context(self.plot.theme.rcParams)
        # Pandas deprecated is_copy, and when we create new dataframes
        # from slices we do not want complaints. We always uses the
        # new frames knowing that they are separate from the original.
        self.pd_option_context = pd.option_context(
            "mode.chained_assignment", None
        )
        self.rc_context.__enter__()
        self.pd_option_context.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """
        Exit matplotlib & pandas environments
        """
        import matplotlib.pyplot as plt

        if exc_type is None:
            if self.show:
                plt.show()
            else:
                plt.close(self.plot.figure)
        else:
            # There is an exception, close any figure
            if hasattr(self.plot, "figure"):
                plt.close(self.plot.figure)

        self.rc_context.__exit__(exc_type, exc_value, exc_traceback)
        self.pd_option_context.__exit__(exc_type, exc_value, exc_traceback)
        delattr(self.plot.theme, "_targets")

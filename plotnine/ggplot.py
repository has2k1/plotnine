from __future__ import annotations

from collections.abc import Sequence
from copy import copy, deepcopy
from io import BytesIO
from itertools import chain
from pathlib import Path
from types import SimpleNamespace as NS
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Iterable,
    Optional,
    cast,
)
from warnings import warn

from ._utils import (
    from_inches,
    is_data_like,
    order_as_data_mapping,
    to_inches,
    ungroup,
)
from ._utils.context import plot_context
from ._utils.ipython import (
    get_display_function,
    get_ipython,
    is_inline_backend,
)
from ._utils.quarto import is_quarto_environment
from .coords import coord_cartesian
from .exceptions import PlotnineError, PlotnineWarning
from .facets import facet_null
from .facets.layout import Layout
from .geoms.geom_blank import geom_blank
from .guides.guides import guides
from .iapi import mpl_save_view
from .layer import Layers
from .mapping.aes import aes, make_labels
from .options import get_option
from .scales.scales import Scales
from .themes.theme import theme, theme_get

if TYPE_CHECKING:
    from typing import Protocol

    from matplotlib.axes import Axes
    from matplotlib.figure import Figure
    from typing_extensions import Self

    from plotnine import watermark
    from plotnine._mpl.gridspec import p9GridSpec
    from plotnine.composition import Compose
    from plotnine.coords.coord import coord
    from plotnine.facets.facet import facet
    from plotnine.layer import layer
    from plotnine.typing import DataLike

    class PlotAddable(Protocol):
        """
        Object that can be added to a ggplot object
        """

        def __radd__(self, other: ggplot) -> ggplot:
            """
            Add to ggplot object

            Parameters
            ----------
            other :
                ggplot object

            Returns
            -------
            :
                ggplot object
            """
            ...


__all__ = ("ggplot", "ggsave", "save_as_pdf_pages")


class ggplot:
    """
    Create a new ggplot object

    Parameters
    ----------
    data :
        Default data for plot. Every layer that does not
        have data of its own will use this one.
    mapping :
        Default aesthetics mapping for the plot. These will be used
        by all layers unless specifically overridden.

    Notes
    -----
    ggplot object only have partial support for pickling. The mappings used
    by pickled objects should not reference variables in the namespace.
    """

    figure: Figure
    axs: list[Axes]
    _gridspec: p9GridSpec

    def __init__(
        self,
        data: Optional[DataLike] = None,
        mapping: Optional[aes] = None,
    ):
        from .mapping._env import Environment

        # Allow some sloppiness
        data, mapping = order_as_data_mapping(data, mapping)
        self.data = data
        self.mapping = mapping if mapping is not None else aes()
        self.facet: facet = facet_null()
        self.labels = make_labels(self.mapping)
        self.layers = Layers()
        self.guides = guides()
        self.scales = Scales()
        self.theme = theme_get()
        self.coordinates: coord = coord_cartesian()
        self.environment = Environment.capture(1)
        self.layout = Layout()
        self.watermarks: list[watermark] = []

        # build artefacts
        self._build_objs = NS()

    def __str__(self) -> str:
        """
        Return a wrapped display size (in pixels) of the plot
        """
        w, h = self.theme._figure_size_px
        return f"<ggplot: ({w} x {h})>"

    def _ipython_display_(self):
        """
        Display plot in the output of the cell

        This method will always be called when a ggplot object is the
        last in the cell.
        """
        self._display()

    def show(self):
        """
        Show plot using the matplotlib backend set by the user

        Users should prefer this method instead of printing or repring
        the object.
        """
        # Prevent against any modifications to the users
        # ggplot object. Do the copy here as we may/may not
        # assign a default theme
        self = deepcopy(self)

        if is_inline_backend() or is_quarto_environment():
            # Take charge of the display because we have to make
            # adjustments for retina output.
            self._display()
        else:
            self.draw(show=True)

    def _display(self):
        """
        Display plot in the cells output

        This function is called for its side-effects.

        It plots the plot to an io buffer, then uses ipython display
        methods to show the result
        """
        ip = get_ipython()
        format = get_option("figure_format") or ip.config.InlineBackend.get(
            "figure_format", "retina"
        )
        # While jpegs can be displayed as retina, we restrict the output
        # of "retina" to png
        if format == "retina":
            self = copy(self)
            self.theme = self.theme.to_retina()

        buf = BytesIO()
        self.save(buf, "png" if format == "retina" else format, verbose=False)
        figure_size_px = self.theme._figure_size_px
        display_func = get_display_function(format, figure_size_px)
        display_func(buf.getvalue())

    def __deepcopy__(self, memo: dict[Any, Any]) -> ggplot:
        """
        Deep copy without copying the dataframe and environment
        """
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        old = self.__dict__
        new = result.__dict__

        # don't make a deepcopy of data
        shallow = {"data", "figure", "gs", "_build_objs"}
        for key, item in old.items():
            if key in shallow:
                new[key] = item
                memo[id(new[key])] = new[key]
            else:
                new[key] = deepcopy(item, memo)

        return result

    def __iadd__(self, other: PlotAddable | list[PlotAddable] | None) -> Self:
        """
        Add other to ggplot object

        Parameters
        ----------
        other :
            Either an object that knows how to "radd"
            itself to a ggplot, or a list of such objects.
        """
        if isinstance(other, Sequence):
            for item in other:
                item.__radd__(self)
        elif other is not None:
            other.__radd__(self)
        return self

    def __add__(
        self,
        rhs: PlotAddable | list[PlotAddable] | None,
    ) -> ggplot:
        """
        Add to ggplot

        Parameters
        ----------
        other :
            Either an object that knows how to "radd"
            itself to a ggplot, or a list of such objects.
        """
        self = deepcopy(self)
        return self.__iadd__(rhs)

    def __or__(self, rhs: ggplot | Compose) -> Compose:
        """
        Compose 2 plots columnwise
        """
        from .composition import Beside

        return Beside([self, rhs])

    def __truediv__(self, rhs: ggplot | Compose) -> Compose:
        """
        Compose 2 plots rowwise
        """
        from .composition import Stack

        return Stack([self, rhs])

    def __sub__(self, rhs: ggplot | Compose) -> Compose:
        """
        Compose 2 plots columnwise
        """
        from .composition import Beside

        return Beside([self, rhs])

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

    def draw(self, *, show: bool = False) -> Figure:
        """
        Render the complete plot

        Parameters
        ----------
        show :
            Whether to show the plot.

        Returns
        -------
        :
            Matplotlib figure
        """
        from ._mpl.layout_manager import PlotnineLayoutEngine

        with plot_context(self, show=show):
            if not hasattr(self, "figure"):
                self._create_figure()
            figure = self.figure

            self._build()

            # setup
            self.axs = self.facet.setup(self)
            self.guides._setup(self)
            self.theme.setup(self)

            # Drawing
            self._draw_layers()
            self._draw_panel_borders()
            self._draw_breaks_and_labels()
            self.guides.draw()
            self._draw_figure_texts()
            self._draw_watermarks()
            self._draw_figure_background()

            # Artist object theming
            self.theme.apply()
            figure.set_layout_engine(PlotnineLayoutEngine(self))

        return figure

    def _create_figure(self):
        """
        Create gridspec for the panels
        """
        import matplotlib.pyplot as plt

        from ._mpl.gridspec import p9GridSpec

        self.figure = plt.figure()
        self._gridspec = p9GridSpec(1, 1, self.figure)

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
        layers.use_defaults_after_scale(scales)

        # Allow stats to modify the layer data
        layers.finish_statistics()

        # Allow layout to modify data before rendering
        layout.finish_data(layers)

    def _draw_panel_borders(self):
        """
        Draw Panel boders
        """
        # We add a patch rather than use ax.patch because want the
        # grid lines below the borders. We leave ax.patch for the
        # background only.
        if self.theme.T.is_blank("panel_border"):
            return

        from matplotlib.patches import Rectangle

        for ax in self.axs:
            rect = Rectangle(
                (0, 0),
                1,
                1,
                facecolor="none",
                transform=ax.transAxes,
                # Adding a clip path but defaulting to no clipping
                # gives a fullwidth border that can perfectly overlap
                # will with legend borders.
                clip_path=ax.patch,
                clip_on=False,
            )
            self.figure.add_artist(rect)
            self.theme.targets.panel_border.append(rect)

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

    def _draw_figure_texts(self):
        """
        Draw title, x label, y label and caption onto the figure
        """
        figure = self.figure
        theme = self.theme
        targets = theme.targets

        title = self.labels.get("title", "")
        subtitle = self.labels.get("subtitle", "")
        caption = self.labels.get("caption", "")
        tag = self.labels.get("tag", "")

        # Get the axis labels (default or specified by user)
        # and let the coordinate modify them e.g. flip
        labels = self.coordinates.labels(
            self.layout.set_xy_labels(self.labels)
        )

        # The locations are handled by the layout manager
        if title:
            targets.plot_title = figure.text(0, 0, title)

        if subtitle:
            targets.plot_subtitle = figure.text(0, 0, subtitle)

        if caption:
            targets.plot_caption = figure.text(0, 0, caption)

        if tag:
            targets.plot_tag = figure.text(0, 0, tag)

        if labels.x:
            targets.axis_title_x = figure.text(0, 0, labels.x)

        if labels.y:
            targets.axis_title_y = figure.text(0, 0, labels.y)

    def _draw_watermarks(self):
        """
        Draw watermark onto figure
        """
        for wm in self.watermarks:
            wm.draw(self.figure)

    def _draw_figure_background(self):
        from matplotlib.patches import Rectangle

        rect = Rectangle((0, 0), 0, 0, facecolor="none", zorder=-1000)
        self.figure.add_artist(rect)
        self._gridspec.patch = rect
        self.theme.targets.plot_background = rect

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

    def _update_labels(self, layer: layer):
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
        filename: Optional[str | Path | BytesIO] = None,
        format: Optional[str] = None,
        path: Optional[str] = None,
        width: Optional[float] = None,
        height: Optional[float] = None,
        units: str = "in",
        dpi: Optional[float] = None,
        limitsize: bool | None = None,
        verbose: bool = True,
        **kwargs: Any,
    ) -> mpl_save_view:
        """
        Create MPL figure that will be saved

        Notes
        -----
        This method has the same arguments as [](`~plotnine.ggplot.save`).
        Use it to get access to the figure that will be saved.
        """
        fig_kwargs: Dict[str, Any] = {"format": format, **kwargs}

        if limitsize is None:
            limitsize = cast("bool", get_option("limitsize"))

        # filename, depends on the object
        if filename is None:
            ext = format if format else "pdf"
            filename = self._save_filename(ext)

        if path and isinstance(filename, (Path, str)):
            filename = Path(path) / filename

        fig_kwargs["fname"] = filename

        # Preserve the users object
        self = deepcopy(self)

        # The figure size should be known by the theme
        if width is not None and height is not None:
            width = to_inches(width, units)
            height = to_inches(height, units)
            self += theme(figure_size=(width, height))
        elif (width is None and height is not None) or (
            width is not None and height is None
        ):
            raise PlotnineError("You must specify both width and height")
        else:
            width, height = cast(
                "tuple[float, float]", self.theme.getp("figure_size")
            )

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
        filename: Optional[str | Path | BytesIO] = None,
        format: Optional[str] = None,
        path: str = "",
        width: Optional[float] = None,
        height: Optional[float] = None,
        units: str = "in",
        dpi: Optional[int] = None,
        limitsize: bool | None = None,
        verbose: bool = True,
        **kwargs: Any,
    ):
        """
        Save a ggplot object as an image file

        Parameters
        ----------
        filename :
            File name to write the plot to. If not specified, a name
            like “plotnine-save-<hash>.<format>” is used.
        format :
            Image format to use, automatically extract from
            file name extension.
        path :
            Path to save plot to (if you just want to set path and
            not filename).
        width :
            Width (defaults to value set by the theme). If specified
            the `height` must also be given.
        height :
            Height (defaults to value set by the theme). If specified
            the `width` must also be given.
        units :
            Units for width and height when either one is explicitly
            specified (in, cm, or mm).
        dpi :
            DPI to use for raster graphics. If None, defaults to using
            the `dpi` of theme, if none is set then a `dpi` of 100.
        limitsize :
            If `True` (the default), save will not save images
            larger than 25x25 inches, to prevent the common error
            of specifying dimensions in pixels. The default value
            is from the option `plotine.options.limitsize`.
        verbose :
            If `True`, print the saving information.
        kwargs :
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

        with plot_context(self).rc_context:
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
    Save multiple [](`~plotnine.ggplot`) objects to a PDF file, one per page.

    Parameters
    ----------
    plots :
        Plot objects to write to file. `plots` may be either a
        collection such as a [](:class:`list`) or [](:class:`set`)

        ```python
        base_plot = ggplot(…)
        plots = [base_plot + ggtitle('%d of 3' % i) for i in range(1, 3)]
        save_as_pdf_pages(plots)
        ```

        or, a generator that yields [](`~plotnine.ggplot`) objects:

        ```python
        def myplots():
            for i in range(1, 3):
                yield ggplot(…) + ggtitle('%d of 3' % i)
        save_as_pdf_pages(myplots())
        ```
    filename :
        File name to write the plot to. If not specified, a name
        like “plotnine-save-<hash>.pdf” is used.
    path :
        Path to save plot to (if you just want to set path and
        not filename).
    verbose :
        If `True`, print the saving information.
    kwargs :
        Additional arguments to pass to
        [](:meth:`~matplotlib.figure.Figure.savefig`).

    Notes
    -----
    Using pandas [](:meth:`~pandas.DataFrame.groupby`) methods, tidy data
    can be "faceted" across pages:

    ```python
    from plotnine.data import mtcars

    def facet_pages(column)
        base_plot = [
            aes(x="wt", y="mpg", label="name"),
            geom_text(),
        ]
        for label, group_data in mtcars.groupby(column):
            yield ggplot(group_data) + base_plot + ggtitle(label)

    save_as_pdf_pages(facet_pages('cyl'))
    ```

    Unlike [](:meth:`~plotnine.ggplot.save`),
    [](:meth:`~plotnine.save_as_pdf_pages`)
    does not process arguments for `height` or `width`. To set the figure
    size, add [](`~plotnine.themes.themeable.figure_size`) to the theme
    for some or all of the objects in `plots`:

    ```python
    plot = ggplot(…)
    # The following are equivalent
    plot.save('filename.pdf', height=6, width=8)
    save_as_pdf_pages([plot + theme(figure_size=(8, 6))])
    ```
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
            with plot_context(plot).rc_context:
                # Save as a page in the PDF file
                pdf.savefig(fig, **fig_kwargs)

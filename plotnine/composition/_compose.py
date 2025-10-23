from __future__ import annotations

import abc
from copy import copy, deepcopy
from io import BytesIO
from typing import TYPE_CHECKING, cast, overload

from plotnine.themes.theme import theme, theme_get

from .._utils.context import plot_composition_context
from .._utils.ipython import (
    get_ipython,
    get_mimebundle,
    is_inline_backend,
)
from .._utils.quarto import is_knitr_engine, is_quarto_environment
from ..composition._plot_annotation import plot_annotation
from ..composition._plot_layout import plot_layout
from ..composition._types import ComposeAddable, CompositionItems
from ..options import get_option

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Iterator

    from matplotlib.figure import Figure

    from plotnine._mpl.gridspec import p9GridSpec
    from plotnine.ggplot import PlotAddable, ggplot
    from plotnine.typing import FigureFormat, MimeBundle


class Compose:
    """
    Base class for those that create plot compositions

    As a user, you will never directly work with this class, except
    through the operators that it makes possible.
    The operators are of two kinds:

    ### 1. Composing Operators

    The combine plots or compositions into a single composition.
    Both operands are either a plot or a composition.

    `/`

    :   Arrange operands side by side.
        Powered by the subclass [](`~plotnine.composition.Beside`).

    `|`

    :   Arrange operands vertically.
        Powered by the subclass [](`~plotnine.composition.Stack`).

    `-`

    :   Arrange operands side by side _and_ at the same nesting level.
        Also powered by the subclass [](`~plotnine.composition.Beside`).

    `+`

    :   Arrange operands in a 2D grid.
        Powered by the subclass [](`~plotnine.composition.Wrap`).

    ### 2. Plot Modifying Operators

    The modify all or some of the plots in a composition.
    The left operand is a composition and the right operand is a
    _plotaddable_; any object that can be added to a `ggplot` object
    e.g. _geoms_, _stats_, _themes_, _facets_, ... .

    `&`

    :   Add right hand side to all plots in the composition.

    `*`

    :   Add right hand side to all plots in the top-most nesting
        level of the composition.

    `+`

    :    Add right hand side to the last plot in the composition.

    Parameters
    ----------
    items :
        The objects to be arranged (composed)


    See Also
    --------
    plotnine.composition.Beside : To arrange plots side by side
    plotnine.composition.Stack : To arrange plots vertically
    plotnine.composition.Wrap : To arrange in a grid
    plotnine.composition.plot_spacer : To add a blank space between plots
    """

    # These are created in the ._create_figure
    figure: Figure
    _gridspec: p9GridSpec
    """
    Gridspec (1x1) that contains the annotations and the composition items

     -------------------
    |  title            |<----- This one
    |  subtitle         |
    |                   |
    |   -------------   |
    |  |      |      |<-+----- .items._gridspec
    |  |      |      |  |
    |   -------------   |
    |                   |
    |  caption          |
     -------------------

    plot_layout's theme parameter affects this gridspec.
    """

    def __init__(self, items: list[ggplot | Compose]):
        # The way we handle the plots has consequences that would
        # prevent having a duplicate plot in the composition.
        # Using copies prevents this.
        self.items = CompositionItems(
            [op if isinstance(op, Compose) else deepcopy(op) for op in items]
        )

        self._layout = plot_layout()
        """
        Every composition gets initiated with an empty plot_layout whose
        attributes are either dynamically generated before the composition
        is drawn, or they are overwritten by a layout added by the user.
        """

        self._annotation = plot_annotation()
        """
        The annotations around the composition
        """

    def __repr__(self):
        """
        repr

        Notes
        -----
        Subclasses that are dataclasses should be declared with
        `@dataclass(repr=False)`.
        """
        # knitr relies on __repr__ to automatically print the last object
        # in a cell.
        if is_knitr_engine():
            self.show()
            return ""
        return super().__repr__()

    @property
    def layout(self) -> plot_layout:
        """
        The plot_layout of this composition
        """
        self.items
        return self._layout

    @layout.setter
    def layout(self, value: plot_layout):
        """
        Add (or merge) a plot_layout to this composition
        """
        self._layout = copy(self.layout)
        self._layout.update(value)

    @property
    def annotation(self) -> plot_annotation:
        """
        The plot_annotation of this composition
        """
        return self._annotation

    @annotation.setter
    def annotation(self, value: plot_annotation):
        """
        Add (or merge) a plot_annotation to this composition
        """
        self._annotation = copy(self.annotation)
        self._annotation.update(value)

    @property
    def nrow(self) -> int:
        return cast("int", self.layout.nrow)

    @property
    def ncol(self) -> int:
        return cast("int", self.layout.ncol)

    @property
    def theme(self) -> theme:
        """
        Theme for this composition

        This is the default theme plus combined with theme from the
        annotation.
        """
        if not getattr(self, "_theme", None):
            self._theme = theme_get() + self.annotation.theme
        return self._theme

    @theme.setter
    def theme(self, value: theme):
        self._theme = value

    @abc.abstractmethod
    def __or__(self, rhs: ggplot | Compose) -> Compose:
        """
        Add rhs as a column
        """

    @abc.abstractmethod
    def __truediv__(self, rhs: ggplot | Compose) -> Compose:
        """
        Add rhs as a row
        """

    def __add__(
        self,
        rhs: ggplot | Compose | PlotAddable | ComposeAddable,
    ) -> Compose:
        """
        Add rhs to the composition

        Parameters
        ----------
        rhs:
            What to add to the composition
        """
        from plotnine import ggplot

        self = deepcopy(self)

        if isinstance(rhs, ComposeAddable):
            return rhs.__radd__(self)
        elif not isinstance(rhs, (ggplot, Compose)):
            self.last_plot = self.last_plot + rhs
            return self

        t1, t2 = type(self).__name__, type(rhs).__name__
        msg = f"unsupported operand type(s) for +: '{t1}' and '{t2}'"
        raise TypeError(msg)

    def __sub__(self, rhs: ggplot | Compose) -> Compose:
        """
        Add the rhs onto the composition

        Parameters
        ----------
        rhs:
            What to place besides the composition
        """
        from plotnine import ggplot

        from . import Beside

        if not isinstance(rhs, (ggplot, Compose)):
            t1, t2 = type(self).__name__, type(rhs).__name__
            msg = f"unsupported operand type(s) for -: '{t1}' and '{t2}'"
            raise TypeError(msg)

        return Beside([self, rhs])

    def __and__(self, rhs: PlotAddable) -> Compose:
        """
        Add rhs to all plots in the composition

        Parameters
        ----------
        rhs:
            What to add.
        """
        from plotnine import theme

        self = deepcopy(self)

        if isinstance(rhs, theme):
            self.annotation.theme = self.annotation.theme + rhs

        for i, item in enumerate(self):
            if isinstance(item, Compose):
                self[i] = item & rhs
            else:
                item += copy(rhs)

        return self

    def __mul__(self, rhs: PlotAddable) -> Compose:
        """
        Add rhs to the outermost nesting level of the composition

        Parameters
        ----------
        rhs:
            What to add.
        """
        from plotnine import ggplot

        self = deepcopy(self)

        for item in self:
            if isinstance(item, ggplot):
                item += copy(rhs)

        return self

    def __len__(self) -> int:
        """
        Number of operands
        """
        return len(self.items)

    def __iter__(self) -> Iterator[ggplot | Compose]:
        """
        Return an iterable of all the items
        """
        return iter(self.items)

    @overload
    def __getitem__(self, index: int) -> ggplot | Compose: ...

    @overload
    def __getitem__(self, index: slice) -> list[ggplot | Compose]: ...

    def __getitem__(
        self,
        index: int | slice,
    ) -> ggplot | Compose | list[ggplot | Compose]:
        return self.items[index]

    def __setitem__(self, key, value):
        self.items[key] = value

    def _repr_mimebundle_(self, include=None, exclude=None) -> MimeBundle:
        """
        Return dynamic MIME bundle for composition display
        """
        ip = get_ipython()
        format: FigureFormat = (
            get_option("figure_format")
            or (ip and ip.config.InlineBackend.get("figure_format"))
            or "retina"
        )

        if format == "retina":
            self = deepcopy(self)
            self._to_retina()

        buf = BytesIO()
        self.save(buf, "png" if format == "retina" else format)
        figure_size_px = self.theme._figure_size_px
        return get_mimebundle(buf.getvalue(), format, figure_size_px)

    def iter_sub_compositions(self):
        for item in self:
            if isinstance(item, Compose):
                yield item

    def iter_plots(self):
        from plotnine import ggplot

        for item in self:
            if isinstance(item, ggplot):
                yield item

    @property
    def last_plot(self) -> ggplot:
        """
        Last plot added to the composition
        """
        from plotnine import ggplot

        last_operand = self.items[-1]
        if isinstance(last_operand, ggplot):
            return last_operand
        else:
            return last_operand.last_plot

    @last_plot.setter
    def last_plot(self, plot: ggplot):
        """
        Replace the last plot in the composition
        """
        from plotnine import ggplot

        last_operand = self.items[-1]
        if isinstance(last_operand, ggplot):
            self.items[-1] = plot
        else:
            last_operand.last_plot = plot

    def __deepcopy__(self, memo):
        """
        Deep copy without copying the figure
        """
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        old = self.__dict__
        new = result.__dict__

        shallow = {"figure", "gridsspec", "__copy"}
        for key, item in old.items():
            if key in shallow:
                new[key] = item
                memo[id(new[key])] = new[key]
            else:
                new[key] = deepcopy(item, memo)

        old["__copy"] = result

        return result

    def _to_retina(self):
        from plotnine import ggplot

        self.theme = self.theme.to_retina()

        for item in self:
            if isinstance(item, ggplot):
                item.theme = item.theme.to_retina()
            else:
                item._to_retina()

    def _setup(self) -> Figure:
        """
        Setup this instance for the building process
        """
        self._create_figure()
        self._remove_sub_composition_background()
        return self.figure

    def _create_figure(self):
        """
        Create figure & gridspecs for all sub compositions
        """
        if hasattr(self, "figure"):
            return

        import matplotlib.pyplot as plt

        from plotnine._mpl.gridspec import p9GridSpec

        figure = plt.figure()
        self._generate_gridspecs(
            figure, p9GridSpec(1, 1, figure, nest_into=None)
        )

    def _generate_gridspecs(self, figure: Figure, container_gs: p9GridSpec):
        from plotnine import ggplot
        from plotnine._mpl.gridspec import p9GridSpec

        self.figure = figure
        self._gridspec = container_gs
        self.layout._setup(self)
        self.items._gridspec = p9GridSpec.from_layout(
            self.layout, figure=figure, nest_into=container_gs[0]
        )

        # Iterating over the gridspec yields the SubplotSpecs for each
        # "subplot" in the grid. The SubplotSpec is the handle for the
        # area in the grid; it allows us to put a plot or a nested
        # composion in that area.
        for item, subplot_spec in zip(self, self.items._gridspec):
            # This container gs will contain a plot or a composition,
            # i.e. it will be assigned to one of:
            #    1. ggplot._gridspec
            #    2. compose._gridspec
            _container_gs = p9GridSpec(1, 1, figure, nest_into=subplot_spec)
            if isinstance(item, ggplot):
                item.figure = figure
                item._gridspec = _container_gs
            else:
                item._generate_gridspecs(figure, _container_gs)

    def _remove_sub_composition_background(self):
        """
        Remove the background and margins of subcompositions

        Only the top-most composition can have a background and
        margin. This prevents edgy interactions.
        """
        from plotnine import element_blank

        for cmp in self.iter_sub_compositions():
            cmp.theme = cmp.theme + theme(
                plot_margin=0, plot_background=element_blank()
            )

    def show(self):
        """
        Display plot in the cells output

        This function is called for its side-effects.
        """
        # Prevent against any modifications to the users
        # ggplot object. Do the copy here as we may/may not
        # assign a default theme
        self = deepcopy(self)

        if is_inline_backend() or is_quarto_environment():
            from IPython.display import display

            data, metadata = self._repr_mimebundle_()
            display(data, metadata=metadata, raw=True)
        else:
            self.draw(show=True)

    def draw(self, *, show: bool = False) -> Figure:
        """
        Render the arranged plots

        Parameters
        ----------
        show :
            Whether to show the plot.

        Returns
        -------
        :
            Matplotlib figure
        """
        from .._mpl.layout_manager import PlotnineCompositionLayoutEngine

        def _draw(cmp):
            figure = cmp._setup()
            cmp._draw_plots()
            cmp.theme._setup(
                cmp.figure,
                None,
                cmp.annotation.title,
                cmp.annotation.subtitle,
            )
            cmp._draw_annotation()
            cmp._draw_composition_background()

            for sub_cmp in cmp.iter_sub_compositions():
                _draw(sub_cmp)
                sub_cmp.theme.apply()

            return figure

        # As the plot border and plot background apply to the entire
        # composition and not the sub compositions, the theme of the
        # whole composition is applied last (outside _draw).
        with plot_composition_context(self, show):
            figure = _draw(self)
            self.theme.apply()
            figure.set_layout_engine(PlotnineCompositionLayoutEngine(self))

        return figure

    def _draw_plots(self):
        """
        Draw all plots in the composition
        """
        from plotnine import ggplot

        for item in self:
            if isinstance(item, ggplot):
                item.draw()

    def _draw_composition_background(self):
        """
        Draw the background rectangle of the composition
        """
        from matplotlib.patches import Rectangle

        rect = Rectangle((0, 0), 0, 0, facecolor="none", zorder=-1000)
        self.figure.add_artist(rect)
        self._gridspec.patch = rect
        self.theme.targets.plot_background = rect

    def _draw_annotation(self):
        """
        Draw the items in the annotation
        """
        if self.annotation.empty():
            return

        figure = self.theme.figure
        targets = self.theme.targets

        if title := self.annotation.title:
            targets.plot_title = figure.text(0, 0, title)

        if subtitle := self.annotation.subtitle:
            targets.plot_subtitle = figure.text(0, 0, subtitle)

        if caption := self.annotation.caption:
            targets.plot_caption = figure.text(0, 0, caption)

    def save(
        self,
        filename: str | Path | BytesIO,
        format: str | None = None,
        dpi: int | None = None,
        **kwargs,
    ):
        """
        Save a composition as an image file

        Parameters
        ----------
        filename :
            File name to write the plot to. If not specified, a name
        format :
            Image format to use, automatically extract from
            file name extension.
        dpi :
            DPI to use for raster graphics. If None, defaults to using
            the `dpi` of theme to the first plot.
        **kwargs :
            These are ignored. Here to "softly" match the API of
            `ggplot.save()`.
        """
        from plotnine import theme

        # To set the dpi, we only need to change the dpi of
        # the last plot and theme gets added to the last plot
        plot = (self + theme(dpi=dpi)) if dpi else self
        figure = plot.draw()
        figure.savefig(filename, format=format)

from __future__ import annotations

import abc
from copy import copy, deepcopy
from dataclasses import dataclass, field
from io import BytesIO
from typing import TYPE_CHECKING, cast, overload

from .._utils.context import plot_composition_context
from .._utils.ipython import (
    get_ipython,
    get_mimebundle,
    is_inline_backend,
)
from .._utils.quarto import is_knitr_engine, is_quarto_environment
from ..composition._plot_layout import plot_layout
from ..composition._types import ComposeAddable
from ..options import get_option
from ._plotspec import plotspec

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Generator, Iterator

    from matplotlib.figure import Figure

    from plotnine._mpl.gridspec import p9GridSpec
    from plotnine.ggplot import PlotAddable, ggplot
    from plotnine.typing import FigureFormat, MimeBundle


@dataclass
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

    See Also
    --------
    plotnine.composition.Beside : To arrange plots side by side
    plotnine.composition.Stack : To arrange plots vertically
    plotnine.composition.Stack : To arrange in a grid
    plotnine.composition.plot_spacer : To add a blank space between plots
    """

    items: list[ggplot | Compose]
    """
    The objects to be arranged (composed)
    """

    _layout: plot_layout = field(
        init=False, repr=False, default_factory=plot_layout
    )
    """
    Every composition gets initiated with an empty plot_layout whose
    attributes are either dynamically generated before the composition
    is drawn, or they are overwritten by a layout added by the user.
    """

    # These are created in the _create_figure method
    figure: Figure = field(init=False, repr=False)
    plotspecs: list[plotspec] = field(init=False, repr=False)
    gridspec: p9GridSpec = field(init=False, repr=False)

    def __post_init__(self):
        # The way we handle the plots has consequences that would
        # prevent having a duplicate plot in the composition.
        # Using copies prevents this.
        self.items = [
            op if isinstance(op, Compose) else deepcopy(op)
            for op in self.items
        ]

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
        return self._layout

    @layout.setter
    def layout(self, value: plot_layout):
        """
        Add (or merge) a plot_layout to this composition
        """
        if self.has_layout:
            _new_layout = copy(self.layout)
            _new_layout.update(value)
        else:
            _new_layout = value

        self._layout = _new_layout

    @property
    def nrow(self) -> int:
        return cast("int", self.layout.nrow)

    @property
    def ncol(self) -> int:
        return cast("int", self.layout.ncol)

    @property
    def has_layout(self) -> bool:
        return hasattr(self, "_layout")

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
        self = deepcopy(self)

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
        figure_size_px = self.last_plot.theme._figure_size_px
        return get_mimebundle(buf.getvalue(), format, figure_size_px)

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

        for item in self:
            if isinstance(item, ggplot):
                item.theme = item.theme.to_retina()
            else:
                item._to_retina()

    def _create_gridspec(self, figure, nest_into):
        """
        Create the gridspec for this composition
        """
        from plotnine._mpl.gridspec import p9GridSpec

        self._layout._setup(self)

        self.gridspec = p9GridSpec(
            self.nrow, self.ncol, figure, nest_into=nest_into
        )

    def _setup(self) -> Figure:
        """
        Setup this instance for the building process
        """
        if not hasattr(self, "figure"):
            self._create_figure()

        return self.figure

    def _create_figure(self):
        import matplotlib.pyplot as plt

        from plotnine import ggplot
        from plotnine._mpl.gridspec import p9GridSpec

        def _make_plotspecs(
            cmp: Compose, parent_gridspec: p9GridSpec | None
        ) -> Generator[plotspec]:
            """
            Return the plot specification for each subplot in the composition
            """
            # This gridspec contains a composition group e.g.
            # (p2 | p3) of p1 | (p2 | p3)
            ss_or_none = parent_gridspec[0] if parent_gridspec else None
            cmp._create_gridspec(self.figure, ss_or_none)

            # Each subplot in the composition will contain one of:
            #    1. A plot
            #    2. A plot composition
            #    3. Nothing
            # Iterating over the gridspec yields the SubplotSpecs for each
            # "subplot" in the grid. The SubplotSpec is the handle that
            # allows us to set it up for a plot or to nest another gridspec
            # in it.
            for item, subplot_spec in zip(cmp, cmp.gridspec):  # pyright: ignore[reportArgumentType]
                if isinstance(item, ggplot):
                    yield plotspec(
                        item,
                        self.figure,
                        cmp.gridspec,
                        subplot_spec,
                        p9GridSpec(1, 1, self.figure, nest_into=subplot_spec),
                    )
                elif item:
                    yield from _make_plotspecs(
                        item,
                        p9GridSpec(1, 1, self.figure, nest_into=subplot_spec),
                    )

        self.figure = plt.figure()
        self.plotspecs = list(_make_plotspecs(self, None))

    def _draw_plots(self):
        """
        Draw all plots in the composition
        """
        for ps in self.plotspecs:
            ps.plot.draw()

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

        with plot_composition_context(self, show):
            figure = self._setup()
            self._draw_plots()
            figure.set_layout_engine(PlotnineCompositionLayoutEngine(self))
        return figure

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

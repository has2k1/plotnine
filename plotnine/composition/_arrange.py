from __future__ import annotations

import abc
from copy import deepcopy
from dataclasses import dataclass, field
from io import BytesIO
from typing import TYPE_CHECKING

from .._utils.ipython import (
    get_display_function,
    get_ipython,
)
from ..options import get_option
from ._plotspec import plotspec

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Generator, Iterator, Self

    from matplotlib.figure import Figure

    from plotnine._mpl.gridspec import p9GridSpec
    from plotnine._utils.ipython import FigureFormat
    from plotnine.ggplot import PlotAddable, ggplot


@dataclass
class Arrange:
    """
    Base class for those that create plot compositions

    As a user, you will never directly work with this class, except
    the operators [`|`](`plotnine.composition.Beside`) and
    [`/`](`plotnine.composition.Stack`) that are powered by subclasses
    of this class.

    Parameters
    ----------
    operands:
        The objects to be put together (composed).

    See Also
    --------
    plotnine.composition.Beside : To arrange plots side by side
    plotnine.composition.Stack : To arrange plots vertically
    plotnine.composition.plot_spacer : To add a blank space between plots
    """

    operands: list[ggplot | Arrange]

    # These are created in the _create_figure method
    figure: Figure = field(init=False, repr=False)
    plotspecs: list[plotspec] = field(init=False, repr=False)
    gridspec: p9GridSpec = field(init=False, repr=False)

    def __post_init__(self):
        # The way we handle the plots has consequences that would
        # prevent having a duplicate plot in the composition.
        # Using copies prevents this.
        self.operands = [
            op if isinstance(op, Arrange) else deepcopy(op)
            for op in self.operands
        ]

    @abc.abstractmethod
    def __or__(self, rhs: ggplot | Arrange) -> Arrange:
        """
        Add rhs as a column
        """

    @abc.abstractmethod
    def __truediv__(self, rhs: ggplot | Arrange) -> Arrange:
        """
        Add rhs as a row
        """

    def __add__(self, rhs: ggplot | Arrange | PlotAddable) -> Arrange:
        """
        Add rhs to the composition

        Parameters
        ----------
        rhs:
            What to add to the composition
        """
        from plotnine import ggplot

        if not isinstance(rhs, (ggplot, Arrange)):
            cmp = deepcopy(self)
            cmp.last_plot = cmp.last_plot + rhs
            return cmp
        return self.__class__([*self, rhs])

    def __sub__(self, rhs: ggplot | Arrange) -> Arrange:
        """
        Add the rhs onto the composition

        Parameters
        ----------
        rhs:
            What to place besides the composition
        """
        return self.__class__([self, rhs])

    def __and__(self, rhs: PlotAddable) -> Arrange:
        """
        Add rhs to all plots in the composition

        Parameters
        ----------
        rhs:
            What to add.
        """
        self = deepcopy(self)

        def add_other(op: Arrange):
            for item in op:
                if isinstance(item, Arrange):
                    add_other(item)
                else:
                    item += rhs

        add_other(self)
        return self

    def __mul__(self, rhs: PlotAddable) -> Arrange:
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
                item += rhs
        return self

    def __len__(self) -> int:
        """
        Number of operand
        """
        return len(self.operands)

    def __iter__(self) -> Iterator[ggplot | Arrange]:
        """
        Return an iterable of all the operands
        """
        return iter(self.operands)

    def _ipython_display_(self):
        """
        Display plot in the output of the cell
        """
        return self._display()

    @property
    def nrow(self) -> int:
        """
        Number of rows in the composition
        """
        return 0

    @property
    def ncol(self) -> int:
        """
        Number of cols in the composition
        """
        return 0

    @property
    def last_plot(self) -> ggplot:
        """
        Last plot added to the composition
        """
        from plotnine import ggplot

        last_operand = self.operands[-1]
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

        last_operand = self.operands[-1]
        if isinstance(last_operand, ggplot):
            self.operands[-1] = plot
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

        self.gridspec = p9GridSpec(
            self.nrow, self.ncol, figure, nest_into=nest_into
        )

    def _create_figure(self):
        import matplotlib.pyplot as plt

        from plotnine import ggplot
        from plotnine._mpl.gridspec import p9GridSpec

        def _make_plotspecs(
            cmp: Arrange, parent_gridspec: p9GridSpec | None
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

    def _display(self):
        """
        Display plot in the cells output

        This function is called for its side-effects.

        It draws the plot to an io buffer then uses ipython display
        methods to show the result.
        """
        ip = get_ipython()
        format: FigureFormat = get_option(
            "figure_format"
        ) or ip.config.InlineBackend.get("figure_format", "retina")

        if format == "retina":
            self = deepcopy(self)
            self._to_retina()

        buf = BytesIO()
        self.save(buf, "png" if format == "retina" else format)
        figure_size_px = self.last_plot.theme._figure_size_px
        display_func = get_display_function(format, figure_size_px)
        display_func(buf.getvalue())

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
            self._create_figure()
            figure = self.figure

            for ps in self.plotspecs:
                ps.plot.draw()

            self.figure.set_layout_engine(
                PlotnineCompositionLayoutEngine(self)
            )
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
        kwargs :
            These are ignored. Here to "softly" match the API of
            `ggplot.save()`.
        """
        from plotnine import theme

        # To set the dpi, we only need to change the dpi of
        # the last plot and theme gets added to the last plot
        plot = (self + theme(dpi=dpi)) if dpi else self
        figure = plot.draw()
        figure.savefig(filename, format=format)


@dataclass
class plot_composition_context:
    cmp: Arrange
    show: bool

    def __post_init__(self):
        import matplotlib as mpl

        # The dpi is needed when the figure is created, either as
        # a parameter to plt.figure() or an rcParam.
        # https://github.com/matplotlib/matplotlib/issues/24644
        # When drawing the Composition, the dpi themeable is infective
        # because it sets the rcParam after this figure is created.
        rcParams = {"figure.dpi": self.cmp.last_plot.theme.getp("dpi")}
        self._rc_context = mpl.rc_context(rcParams)

    def __enter__(self) -> Self:
        """
        Enclose in matplolib & pandas environments
        """
        self._rc_context.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        import matplotlib.pyplot as plt

        if exc_type is None:
            if self.show:
                plt.show()
            else:
                plt.close(self.cmp.figure)
        else:
            # There is an exception, close any figure
            if hasattr(self.cmp, "figure"):
                plt.close(self.cmp.figure)

        self._rc_context.__exit__(exc_type, exc_value, exc_traceback)

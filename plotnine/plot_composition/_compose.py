from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
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


class Compose:
    """
    Arrange two or more plots

    Parameters
    ----------
    operands:
        The objects to be put together (composed).
    """

    def __init__(self, operands: list[ggplot | Compose]):
        self.operands = operands

        # These are created in the _create_figure method
        self.figure: Figure
        self.plotspecs: list[plotspec]
        self.gridspec: p9GridSpec

    def __add__(self, rhs: ggplot | Compose) -> Compose:
        """
        Add rhs to the composition

        Parameters
        ----------
        rhs:
            What to add to the composition
        """
        return self.__class__([*self, rhs])

    def __sub__(self, rhs: ggplot | Compose) -> Compose:
        """
        Add the rhs besides the composition

        Parameters
        ----------
        rhs:
            What to place besides the composition
        """
        return self.__class__([self, rhs])

    def __and__(self, rhs: PlotAddable) -> Compose:
        """
        Add rhs to all plots in the composition

        Parameters
        ----------
        rhs:
            What to add.
        """
        self = deepcopy(self)

        def add_other(op: Compose):
            for item in op:
                if isinstance(item, Compose):
                    add_other(item)
                else:
                    item += rhs

        add_other(self)
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
                item += rhs
        return self

    def __len__(self) -> int:
        """
        Number of operand
        """
        return len(self.operands)

    def __iter__(self) -> Iterator[ggplot | Compose]:
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
    def last_plot(self):
        """
        Last plot added to the composition
        """
        from plotnine import ggplot

        last_operand = self.operands[-1]
        if isinstance(last_operand, ggplot):
            return last_operand
        else:
            return last_operand.last_plot

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
        Render the composed plots

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
        self, filename: str | Path | BytesIO, save_format: str | None = None
    ):
        figure = self.draw()
        figure.savefig(filename, format=save_format)


@dataclass
class plot_composition_context:
    cmp: Compose
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


class OR(Compose):
    """
    Compose by adding a column
    """

    @property
    def nrow(self) -> int:
        return 1

    @property
    def ncol(self) -> int:
        return len(self)

    def __or__(self, rhs: ggplot | Compose) -> Compose:
        """
        Add rhs as a column
        """
        # This is an adjacent or i.e. (OR | rhs) so we collapse the
        # operands into a single operation
        return OR([*self, rhs])

    def __truediv__(self, rhs: ggplot | Compose) -> Compose:
        """
        Add rhs as a row
        """
        return DIV([self, rhs])


class DIV(Compose):
    """
    Compose by adding a row
    """

    @property
    def nrow(self) -> int:
        return len(self)

    @property
    def ncol(self) -> int:
        return 1

    def __truediv__(self, rhs: ggplot | Compose) -> Compose:
        """
        Add rhs as a row
        """
        # This is an adjacent div i.e. (DIV | rhs) so we collapse the
        # operands into a single operation
        return DIV([*self, rhs])

    def __or__(self, rhs: ggplot | Compose) -> Compose:
        """
        Add rhs as a column
        """
        return OR([self, rhs])


class ADD(Compose):
    """
    Compose by adding
    """

    @property
    def nrow(self) -> int:
        from plotnine.facets.facet_wrap import wrap_dims

        return wrap_dims(len(self))[0]

    @property
    def ncol(self) -> int:
        from plotnine.facets.facet_wrap import wrap_dims

        return wrap_dims(len(self))[1]

    def __add__(self, rhs: ggplot | Compose) -> Compose:
        """
        Add rhs to the Composed group
        """
        return ADD([*self, rhs])

    def __or__(self, rhs: ggplot | Compose) -> Compose:
        """
        Add rhs as a column
        """
        return OR([self, rhs])

    def __truediv__(self, rhs: ggplot | Compose) -> Compose:
        """
        Add rhs as a row
        """
        return DIV([self, rhs])

    def __sub__(self, rhs: ggplot | Compose) -> Compose:
        """
        Add rhs as a column
        """
        return OR([self, rhs])

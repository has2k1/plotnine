from __future__ import annotations

from contextlib import nullcontext
from copy import deepcopy
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from narwhals.dependencies import get_pandas
from packaging.version import Version

from ..session import set_last_plot

if TYPE_CHECKING:
    from contextlib import AbstractContextManager
    from typing import Any, Self

    from matplotlib.axes import Axes

    from plotnine import ggplot
    from plotnine._mpl.figure import p9Figure
    from plotnine._mpl.gridspec import p9GridSpec
    from plotnine.composition import Compose


def _pandas_copy_on_write() -> AbstractContextManager[Any]:
    """
    Context in which pandas<3 uses copy-on-write

    Only if pandas is in use, i.e. it has been imported.
    """
    pd = get_pandas()
    if pd is not None and Version(pd.__version__) < Version("3.0"):
        return pd.option_context("mode.copy_on_write", True)
    return nullcontext()


@dataclass
class draw_context:
    """
    Context within which a plot or composition is built

    Parameters
    ----------
    obj :
        ggplot or composition object to be built within the context.
    show :
        Whether to show the plot.
    """

    obj: ggplot | Compose
    show: bool = False
    _pd_context: AbstractContextManager[Any] = field(
        default_factory=nullcontext, init=False, repr=False
    )

    def __post_init__(self):
        import matplotlib as mpl

        # rc_context nests. A composition enters its rcParams, then each plot
        # in it enters and exits its own, so a plot's value, such as a dpi
        # that differs from the composition's, applies only while that plot
        # draws. The composition owns the figure, so its dpi is the one in
        # effect when the figure is created.
        self._rc_context = mpl.rc_context(self.obj.theme.rcParams)
        self._pd_context = _pandas_copy_on_write()

    def __enter__(self) -> Self:
        """
        Enclose in matplotlib & pandas environments
        """

        self._last_plot = deepcopy(self.obj)
        self._rc_context.__enter__()
        self._pd_context.__enter__()

        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """
        Exit matplotlib & pandas environments

        Close the figure on exit only when the object owns it. A child
        drawing into a figure handed down by a parent composition or
        host plot leaves closing to the figure's owner.
        """
        import matplotlib.pyplot as plt

        # The figure may not exist if the draw raised during setup.
        figure = getattr(self.obj, "figure", None)

        if exc_type is None:
            if self.show:
                if figure is not None and is_closed(figure):
                    reopen(figure)
                plt.show()
            elif figure is not None and figure._owner is self.obj:
                plt.close(figure)
            set_last_plot(self._last_plot)
        elif figure is not None:
            # There is an exception, close any figure
            plt.close(figure)

        self._rc_context.__exit__(exc_type, exc_value, exc_traceback)
        self._pd_context.__exit__(exc_type, exc_value, exc_traceback)


@dataclass
class save_context:
    """
    Context within which a drawn figure is saved

    Saving happens after the draw's own context has exited, so the
    object's theme rcParams (fonts, dpi, ...) must be re-applied for
    `savefig` to render the file the same way the figure was drawn.

    Parameters
    ----------
    obj :
        ggplot or composition whose theme rcParams to apply.
    """

    obj: ggplot | Compose

    def __post_init__(self):
        import matplotlib as mpl

        self._rc_context = mpl.rc_context(self.obj.theme.rcParams)

    def __enter__(self) -> Self:
        """
        Enclose in the matplotlib environment
        """
        self._rc_context.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """
        Exit the matplotlib environment
        """
        self._rc_context.__exit__(exc_type, exc_value, exc_traceback)


@dataclass
class _FigureState:
    """
    Figure of a plot or composition, with the gridspecs and axes on it

    Every field belongs to one figure. A plot or composition given a new
    figure replaces the whole object, so no gridspec or axes from the
    previous figure survive, and a copy of the plot or composition starts
    without one.
    """

    figure: p9Figure
    """
    Figure the plot or composition draws into
    """

    gridspec: p9GridSpec | None = None
    """
    Gridspec (1x1) that contains the whole plot or composition

    `None` while an object given only a figure, such as an inset, has yet
    to lay out its own.
    """

    sub_gridspec: p9GridSpec | None = None
    """
    Gridspec (nxn) that contains a plot's facet panels or a composition's
    items

    `None` until they are laid out.

     -------------------------
    |  title                  |<----- .gridspec
    |  subtitle               |
    |                         |
    |   -------------         |
    |  |      |      |<-------+------ .sub_gridspec
    |  |      |      |        |
    |  |      |      | legend |
    |   -------------         |
    |                         |
    |                 caption |
    |-------------------------|
    |          footer         |
     -------------------------
    """

    axs: list[Axes] | None = None
    """
    Panel axes

    `None` until the panels are laid out, and always `None` for a
    composition, whose panels belong to its plots.
    """


def reopen(fig):
    """
    Reopen a matplotlib figure closed with `plt.close`

    A closed figure cannot be shown with `plt.show` until it is reopened.
    """
    from matplotlib._pylab_helpers import Gcf

    Gcf.set_active(fig.canvas.manager)


def is_closed(fig) -> bool:
    """
    Return whether the figure is closed
    """
    import matplotlib.pyplot as plt

    return not plt.fignum_exists(fig.number)


def assign_figure(
    obj: ggplot | Compose,
    figure: p9Figure,
    gridspec: p9GridSpec | None = None,
) -> None:
    """
    Assign a figure to a plot or composition

    Close the object's current figure when the object owns it. Replace the
    object's figure state so nothing bound to the previous figure survives
    the handover.

    Parameters
    ----------
    obj :
        Plot or composition that receives the figure.
    figure :
        Figure that `obj` will draw into.
    gridspec :
        Gridspec that `obj` will use. Leave unset when `obj` must create its
        own, such as when an inset supplies only the figure.
    """
    import matplotlib.pyplot as plt

    if (
        hasattr(obj, "_figure_state")
        and obj._figure_state.figure._owner is obj
        and not is_closed(obj._figure_state.figure)
    ):
        plt.close(obj._figure_state.figure)

    obj._figure_state = _FigureState(figure, gridspec)

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import pandas as pd
from packaging.version import Version

from ..session import set_last_plot

if TYPE_CHECKING:
    from contextlib import AbstractContextManager
    from typing import Self

    from plotnine import ggplot
    from plotnine._mpl.figure import p9Figure
    from plotnine._mpl.gridspec import p9GridSpec
    from plotnine.composition import Compose

PANDAS_LT_3 = Version(pd.__version__) < Version("3.0")


def reopen(fig):
    """
    Reopen an MPL figure that has been closed with plt.close

    A closed figure cannot be shown with plt.show. Only the figure's owner
    closes it, but a user may have closed the window themselves before
    compose.show() runs.
    """
    from matplotlib._pylab_helpers import Gcf

    Gcf.set_active(fig.canvas.manager)


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
    _pd_context: AbstractContextManager[object] | None = field(
        default=None, init=False, repr=False
    )

    def __post_init__(self):
        import matplotlib as mpl

        # rc_context nests. A composition enters its rcParams, then each plot
        # in it enters and exits its own, so a plot's value, such as a dpi
        # that differs from the composition's, applies only while that plot
        # draws. The composition owns the figure, so its dpi is the one in
        # effect when the figure is created.
        self._rc_context = mpl.rc_context(self.obj.theme.rcParams)
        if PANDAS_LT_3:
            self._pd_context = pd.option_context(
                "mode.copy_on_write",
                True,
            )

    def __enter__(self) -> Self:
        """
        Enclose in matplotlib & pandas environments
        """

        self._last_plot = deepcopy(self.obj)
        self._rc_context.__enter__()
        if self._pd_context is not None:
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
        if self._pd_context is not None:
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

    Close the object's current figure when the object owns it. Clear axes and
    gridspec state associated with the previous figure.

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
        hasattr(obj, "figure")
        and obj.figure._owner is obj
        and not is_closed(obj.figure)
    ):
        plt.close(obj.figure)

    obj.figure = figure
    if gridspec is not None:
        obj._gridspec = gridspec
    elif hasattr(obj, "_gridspec"):
        # A gridspec is bound to the figure it was created for; without a
        # replacement, the stale one must not survive the handover.
        delattr(obj, "_gridspec")

    if hasattr(obj, "axs"):
        delattr(obj, "axs")
        delattr(obj, "_sub_gridspec")

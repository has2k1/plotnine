from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from typing_extensions import Self

    from plotnine import ggplot
    from plotnine.composition import Compose


def reopen(fig):
    """
    Reopen an MPL figure that has been closed with plt.close

    When drawing compositions, plot_composition_context will nest
    plot_context. In this case, plot_context may close an MPL figure
    that belongs to composition. A closed figure cannot be shown with
    plt.show, so for compositions compose.show (if called) will do nothing.
    """
    from matplotlib._pylab_helpers import Gcf

    Gcf.set_active(fig.canvas.manager)


def is_closed(fig) -> bool:
    """
    Return True if figure is closed
    """
    import matplotlib.pyplot as plt

    return not plt.fignum_exists(fig.number)


class plot_context:
    """
    Context within which the plot is built

    Parameters
    ----------
    plot :
        ggplot object to be built within the context.
    show :
        Whether to show the plot.
    """

    def __init__(self, plot: ggplot, show: bool = False):
        import matplotlib as mpl

        self.plot = plot
        self.show = show

        # Contexts
        self.rc_context = mpl.rc_context(plot.theme.rcParams)
        # TODO: Remove this context when copy-on-write is permanent, i.e.
        # pandas >= 3.0
        self.pd_option_context = pd.option_context(
            "mode.copy_on_write",
            True,
        )

    def __enter__(self) -> Self:
        """
        Enclose in matplolib & pandas environments
        """

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


@dataclass
class plot_composition_context:
    """
    Context within which a plot composition is built

    Parameters
    ----------
    cmp :
        composition object to be built within the context.
    show :
        Whether to show the plot.
    """

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
                if is_closed(self.cmp.figure):
                    reopen(self.cmp.figure)
                plt.show()
            else:
                plt.close(self.cmp.figure)
        else:
            # There is an exception, close any figure
            if hasattr(self.cmp, "figure"):
                plt.close(self.cmp.figure)

        self._rc_context.__exit__(exc_type, exc_value, exc_traceback)

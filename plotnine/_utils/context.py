from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from typing_extensions import Self

    from plotnine import ggplot


class plot_context:
    """
    Context to setup the environment within with the plot is built

    Parameters
    ----------
    plot :
        ggplot object to be built within the context.
        exits.
    show :
        Whether to show the plot.
    """

    def __init__(self, plot: ggplot, show: bool = False):
        import matplotlib as mpl

        self.plot = plot
        self.show = show

        # Contexts
        self.rc_context = mpl.rc_context(plot.theme.rcParams)
        # Pandas deprecated is_copy, and when we create new dataframes
        # from slices we do not want complaints. We always uses the
        # new frames knowing that they are separate from the original.
        self.pd_option_context = pd.option_context(
            "mode.chained_assignment",
            None,
            "mode.copy_on_write",
            False,
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

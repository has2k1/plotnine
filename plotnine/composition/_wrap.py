from __future__ import annotations

from plotnine.composition._plot_layout import plot_layout
from plotnine.ggplot import ggplot

from ._compose import Compose


class Wrap(Compose):
    """
    Wrap plots or compositions into a grid

    **Usage**

        plot + plot
        plot + composition
        composition + plot
        composition + composition

    Typically, you will use this class through the `+` operator.

    Parameters
    ----------
    items:
        The objects to be arranged (composed)
    nrow:
        Number of rows in the composition
    ncol:
        Number of cols in the composition

    See Also
    --------
    plotnine.composition.Beside : To arrange plots side by side
    plotnine.composition.Stack : To arrange plots vertically
    plotnine.composition.plot_spacer : To add a blank space between plots
    plotnine.composition.Compose : For more on composing plots
    """

    def __init__(
        self,
        items: list[ggplot | Compose],
        *,
        nrow: int | None = None,
        ncol: int | None = None,
    ):
        self.items = items
        super().__post_init__()
        self._wrap_plots(nrow, ncol)

    def _wrap_plots(self, nrow: int | None, ncol: int | None):
        """
        Wrap plots (and subcompositions) into rows and columns
        """
        from plotnine.facets.facet_wrap import wrap_dims

        self.nrow, self.ncol = wrap_dims(len(self), nrow, ncol)

    def __add__(self, rhs):
        """
        Add rhs
        """
        if isinstance(rhs, plot_layout) and (rhs.nrow or rhs.ncol):
            self._wrap_plots(rhs.nrow, rhs.ncol)

        if not isinstance(rhs, (ggplot, Compose)):
            return super().__add__(rhs)

        return Wrap([*self, rhs])

    def __or__(self, rhs: ggplot | Compose) -> Compose:
        """
        Add rhs as a column
        """
        from ._beside import Beside

        return Beside([self, rhs])

    def __truediv__(self, rhs: ggplot | Compose) -> Compose:
        """
        Add rhs as a row
        """
        from ._stack import Stack

        return Stack([self, rhs])

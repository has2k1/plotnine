from __future__ import annotations

from ..ggplot import ggplot
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
    To set the number of rows or columns, add a
    [](`~plotnine.composition.plot_layout`) e.g.
    `p1 + p2 + p3 + plot_layout(nrow=2)`.

    Parameters
    ----------
    items:
        The objects to be arranged (composed)

    See Also
    --------
    plotnine.composition.Beside : To arrange plots side by side
    plotnine.composition.Stack : To arrange plots vertically
    plotnine.composition.plot_spacer : To add a blank space between plots
    plotnine.composition.Compose : For more on composing plots
    """

    def __add__(self, rhs):
        """
        Add rhs into the wrapping composition
        """
        if not isinstance(rhs, (ggplot, Compose)):
            return super().__add__(rhs)

        return Wrap([*self, rhs]) + self.layout + self.annotation

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

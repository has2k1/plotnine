from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ._compose import Compose

if TYPE_CHECKING:
    from plotnine.ggplot import ggplot


@dataclass(repr=False)
class Beside(Compose):
    """
    Place plots or compositions side by side

    **Usage**

        plot | plot
        plot | composition
        composition | plot
        composition | composition

    Typically, you will use this class through the `|` operator.

    See Also
    --------
    plotnine.composition.Stack : To arrange plots vertically
    plotnine.composition.Wrap : To arrange plots in a grid
    plotnine.composition.plot_spacer : To add a blank space between plots
    plotnine.composition.Compose : For more on composing plots
    """

    def __or__(self, rhs: ggplot | Compose) -> Compose:
        """
        Add rhs as a column
        """
        # This is adjacent or i.e. (OR | rhs) so we collapse the
        # operands into a single operation
        return Beside([*self, rhs]) + self.layout

    def __truediv__(self, rhs: ggplot | Compose) -> Compose:
        """
        Add rhs as a row
        """
        from ._stack import Stack

        return Stack([self, rhs])

    def __add__(self, rhs):
        """
        Add rhs into the besides composition
        """
        from plotnine import ggplot

        if not isinstance(rhs, (ggplot, Compose)):
            return super().__add__(rhs)

        return self | rhs

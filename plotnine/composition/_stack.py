from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..composition._plot_layout import plot_layout
from ._compose import Compose

if TYPE_CHECKING:
    from plotnine.ggplot import ggplot


@dataclass(repr=False)
class Stack(Compose):
    """
    Place plots or compositions on top of each other

    **Usage**

        plot / plot
        plot / composition
        composition / plot
        composition / composition

    Typically, you will use this class through the `/` operator.

    See Also
    --------
    plotnine.composition.Beside : To arrange plots side by side
    plotnine.composition.Wrap : To arrange plots in a grid
    plotnine.composition.plot_spacer : To add a blank space between plots
    plotnine.composition.Compose : For more on composing plots
    """

    def __truediv__(self, rhs: ggplot | Compose) -> Compose:
        """
        Add rhs as a row
        """
        # This is an adjacent div i.e. (DIV | rhs) so we collapse the
        # operands into a single operation
        return Stack([*self, rhs]) + self.layout

    def __or__(self, rhs: ggplot | Compose) -> Compose:
        """
        Add rhs as a column
        """
        from ._beside import Beside

        return Beside([self, rhs])

    def _finalise_layout(self):
        if not self.has_layout:
            self.layout = plot_layout()

        if self.layout.nrow is None:
            self.layout.nrow = len(self)
        elif self.layout.nrow < len(self):
            raise ValueError(
                "Specified fewer rows than the items in the composition."
            )

        if self.layout.ncol is None:
            self.layout.ncol = 1

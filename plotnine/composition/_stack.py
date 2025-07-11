from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ._compose import Compose

if TYPE_CHECKING:
    from plotnine.ggplot import ggplot


@dataclass
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
    plotnine.composition.plot_spacer : To add a blank space between plots
    plotnine.composition.Compose : For more on composing plots
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
        return Stack([*self, rhs])

    def __or__(self, rhs: ggplot | Compose) -> Compose:
        """
        Add rhs as a column
        """
        from ._beside import Beside

        return Beside([self, rhs])

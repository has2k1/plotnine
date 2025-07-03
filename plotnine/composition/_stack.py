from __future__ import annotations

from typing import TYPE_CHECKING

from ._arrange import Arrange

if TYPE_CHECKING:
    from plotnine.ggplot import ggplot


class Stack(Arrange):
    """
    Place plots or compositions on top of each other

    **Usage**

        plot / plot
        plot / composition
        composition / plot
        composition / composition

    Typically, you will use this class through the `/` operator.
    """

    @property
    def nrow(self) -> int:
        return len(self)

    @property
    def ncol(self) -> int:
        return 1

    def __truediv__(self, rhs: ggplot | Arrange) -> Arrange:
        """
        Add rhs as a row
        """
        # This is an adjacent div i.e. (DIV | rhs) so we collapse the
        # operands into a single operation
        return Stack([*self, rhs])

    def __or__(self, rhs: ggplot | Arrange) -> Arrange:
        """
        Add rhs as a column
        """
        from ._beside import Beside

        return Beside([self, rhs])

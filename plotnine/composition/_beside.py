from __future__ import annotations

from typing import TYPE_CHECKING

from ._arrange import Arrange

if TYPE_CHECKING:
    from plotnine.ggplot import ggplot


class Beside(Arrange):
    """
    Place plots or compositions side by side

    **Usage**

        plot | plot
        plot | composition
        composition | plot
        composition | composition

    Typically, you will use this class through the `|` operator.
    """

    @property
    def nrow(self) -> int:
        return 1

    @property
    def ncol(self) -> int:
        return len(self)

    def __or__(self, rhs: ggplot | Arrange) -> Arrange:
        """
        Add rhs as a column
        """
        # This is adjacent or i.e. (OR | rhs) so we collapse the
        # operands into a single operation
        return Beside([*self, rhs])

    def __truediv__(self, rhs: ggplot | Arrange) -> Arrange:
        """
        Add rhs as a row
        """
        from ._stack import Stack

        return Stack([self, rhs])

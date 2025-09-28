from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from plotnine import ggplot
    from plotnine._mpl.gridspec import p9GridSpec

    from ._compose import Compose


class ComposeAddable:
    """
    Object that can be added to a ggplot object
    """

    def __radd__(self, other: Compose) -> Compose:
        """
        Add to compose object

        Parameters
        ----------
        other :
            Compose object

        Returns
        -------
        :
            Compose object
        """
        return other


class CompositionItems(list["ggplot | Compose"]):
    """
    The items in a composition
    """

    _gridspec: p9GridSpec
    """
    Gridspec (nxm) that contains the composition items

    plot_layout's widths & heights parameters affect this gridspec.
    """

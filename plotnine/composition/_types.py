from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
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

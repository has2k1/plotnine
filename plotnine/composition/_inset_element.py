from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from ..ggplot import ggplot
    from ._compose import Compose


@dataclass
class inset_element:
    """
    Place a plot as an inset within another plot

    The inset is rendered on top of the host. Adding an `inset_element`
    to a composition attaches it to the most recently added plot in that
    composition.

    Parameters
    ----------
    obj :
        The object to render as an inset.
    left, bottom, right, top :
        Bounding box of the inset in normalised parent coordinates,
        in the range ``[0, 1]``. The bottom-left corner of the region
        selected by `align_to` is ``(0, 0)`` and the top-right is
        ``(1, 1)``.
    align_to :
        Which region of the host plot the bounding box is relative to:

        - ``"panel"`` — the data area only (default).
        - ``"plot"``  — the panel plus axes, labels, and plot margins.
        - ``"full"``  — everything the host plot occupies, including
          any titles, captions, and legends.
    """

    obj: ggplot | Compose
    left: float
    bottom: float
    right: float
    top: float
    align_to: Literal["panel", "plot", "full"] = "panel"

    def __post_init__(self):
        from ..ggplot import ggplot
        from ._compose import Compose

        if not isinstance(self.obj, (ggplot, Compose)):
            raise TypeError(
                "inset_element requires a ggplot or Compose, got "
                f"{type(self.obj).__name__!r}."
            )

        if not 0.0 <= self.left < self.right <= 1.0:
            raise ValueError(
                "inset_element requires 0.0 <= left < right <= 1.0, got "
                f"left={self.left!r}, right={self.right!r}."
            )

        if not 0.0 <= self.bottom < self.top <= 1.0:
            raise ValueError(
                "inset_element requires 0.0 <= bottom < top <= 1.0, got "
                f"bottom={self.bottom!r}, top={self.top!r}."
            )

    def __radd__(self, other: ggplot) -> ggplot:
        """
        Attach this inset to a ggplot
        """
        other._insets.append(deepcopy(self))
        return other

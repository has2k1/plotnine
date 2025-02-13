from __future__ import annotations

from copy import deepcopy

from plotnine import element_rect, ggplot, theme, theme_void


class spacer(ggplot):
    """
    An empty plot
    """

    def __init__(self):
        super().__init__()
        self.theme = theme_void()

    def __add__(self, rhs) -> spacer:  # pyright: ignore[reportIncompatibleMethodOverride]
        """
        Add to spacer

        All added objects are no ops except the plot_background,
        i.e.:

            theme(plot_background=element_rect(fill="red"))
        """
        self = deepcopy(self)
        if isinstance(rhs, theme):
            fill = rhs.getp(("plot_background", "facecolor"))
            self.theme += theme(
                plot_background=element_rect(fill=fill),
            )
        return self

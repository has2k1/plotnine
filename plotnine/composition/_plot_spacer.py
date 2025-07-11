from __future__ import annotations

from copy import deepcopy

from plotnine import element_rect, ggplot, theme, theme_void


class plot_spacer(ggplot):
    """
    Blank area as wide or as tall as a plot

    Parameters
    ----------
    fill :
        Background color. The default is a transparent area, but it
        can be changed through this parameter.

        The color can also be modified by adding a [](`~plotnine.theme`)
        and setting the [](`~plotnine.themes.themeable.plot_background`).

    See Also
    --------
    plotnine.composition.Beside : To arrange plots side by side
    plotnine.composition.Stack : To arrange plots vertically
    plotnine.composition.Compose : For more on composing plots
    """

    def __init__(
        self,
        fill: (
            str
            | tuple[float, float, float]
            | tuple[float, float, float, float]
            | None
        ) = None,
    ):
        super().__init__()
        self.theme = theme_void()
        if fill:
            self.theme += theme(plot_background=element_rect(fill=fill))

    def __add__(self, rhs) -> plot_spacer:
        """
        Add to spacer

        All added objects are no ops except the `plot_background` in
        in a theme.
        """
        self = deepcopy(self)
        if isinstance(rhs, theme):
            fill = rhs.getp(("plot_background", "facecolor"))
            self.theme += theme(
                plot_background=element_rect(fill=fill),
            )
        return self

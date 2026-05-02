from __future__ import annotations

from typing import TYPE_CHECKING

from plotnine import element_rect, ggplot, theme, theme_void

if TYPE_CHECKING:
    from typing_extensions import Self

    from plotnine.ggplot import PlotAddable


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
    alpha :
        Opacity of the background fill, between 0 (transparent) and 1
        (opaque). The default leaves the area transparent.

        The opacity can also be modified by adding a [](`~plotnine.theme`)
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
        alpha: float | None = None,
    ):
        super().__init__()
        self.theme = theme_void() + theme(
            plot_background=element_rect(fill=fill, alpha=alpha)
        )

    def __iadd__(self, rhs: PlotAddable | list[PlotAddable] | None) -> Self:
        """
        Add to spacer

        Only the `plot_background` of a [](`~plotnine.theme`) on the
        right-hand side is merged into the spacer's own theme; every
        other addable is dropped so the spacer keeps its blank
        appearance.
        """
        if isinstance(rhs, theme):
            fill = rhs.getp(("plot_background", "facecolor"))
            alpha = rhs.getp(("plot_background", "alpha"))
            self.theme += theme(
                plot_background=element_rect(fill=fill, alpha=alpha)
            )
        return self

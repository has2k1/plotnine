from .elements import element_blank
from .theme import theme
from .theme_bw import theme_bw


class theme_minimal(theme_bw):
    """
    A minimalistic theme with no background annotations

    Parameters
    ----------
    base_size : int
        Base font size. All text sizes are a scaled versions of
        the base font size.
    base_family : str
        Base font family. If `None`, use [](`plotnine.options.base_family`).
    """

    def __init__(self, base_size=11, base_family=None):
        super().__init__(base_size, base_family)
        self += theme(
            axis_ticks=element_blank(),
            legend_background=element_blank(),
            legend_key=element_blank(),
            panel_background=element_blank(),
            panel_border=element_blank(),
            plot_background=element_blank(),
            strip_background=element_blank(),
        )

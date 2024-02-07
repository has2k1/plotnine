from .elements import element_blank, element_line, element_rect
from .theme import theme
from .theme_bw import theme_bw


class theme_classic(theme_bw):
    """
    A classic-looking theme, with x & y axis lines and no gridlines

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
            panel_border=element_blank(),
            axis_line=element_line(color="black"),
            panel_grid_major=element_blank(),
            panel_grid_minor=element_blank(),
            strip_background=element_rect(colour="black", fill="none", size=1),
            legend_key=element_blank(),
        )

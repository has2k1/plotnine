from .elements import element_blank, element_line, element_rect, element_text
from .theme import theme
from .theme_bw import theme_bw


class theme_linedraw(theme_bw):
    """
    A theme with only black lines of various widths on white backgrounds

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
            axis_text=element_text(color="black", size=base_size * 0.8),
            axis_ticks=element_line(color="black", size=0.5),
            axis_ticks_minor=element_blank(),
            legend_key=element_rect(color="black", size=0.72),
            panel_background=element_rect(fill="white"),
            panel_border=element_rect(fill="none", color="black", size=1),
            panel_grid_major=element_line(color="black", size=0.1),
            panel_grid_minor=element_line(color="black", size=0.02),
            strip_background=element_rect(fill="black", color="black", size=1),
            strip_text_x=element_text(color="white"),
            strip_text_y=element_text(color="white", angle=-90),
        )

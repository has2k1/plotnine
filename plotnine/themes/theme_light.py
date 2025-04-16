from .elements import element_blank, element_line, element_rect, element_text
from .theme import theme
from .theme_gray import theme_gray


class theme_light(theme_gray):
    """
    A theme similar to [](`~plotnine.themes.theme_linedraw.theme_linedraw`)

    Has light grey lines lines and axes to direct more attention
    towards the data.

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
            axis_ticks=element_line(color="#B3B3B3", size=0.5),
            axis_ticks_minor=element_blank(),
            legend_key=element_rect(color="#7F7F7F", size=0.72),
            panel_background=element_rect(fill="white"),
            panel_border=element_rect(fill="none", color="#B3B3B3", size=1),
            panel_grid_major=element_line(color="#D9D9D9", size=0.5),
            panel_grid_minor=element_line(color="#EDEDED", size=0.25),
            strip_background=element_rect(
                fill="#B3B3B3", color="#B3B3B3", size=1
            ),
            strip_text_x=element_text(color="white"),
            strip_text_y=element_text(color="white", angle=-90),
        )

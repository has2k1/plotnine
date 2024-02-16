from .elements import element_blank, element_line, element_rect, element_text
from .theme import theme
from .theme_gray import theme_gray


class theme_dark(theme_gray):
    """
    The dark cousin of [](`~plotnine.themes.theme_light.theme_light`)

    It has  similar line sizes but a dark background. Useful to
    make thin colored lines pop out.

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
            axis_ticks=element_line(color="#666666", size=0.5),
            axis_ticks_minor=element_blank(),
            legend_key=element_rect(fill="#7F7F7F", color="#666666", size=0.5),
            panel_background=element_rect(fill="#7F7F7F", color="none"),
            panel_grid_major=element_line(color="#666666", size=0.5),
            panel_grid_minor=element_line(color="#737373", size=0.25),
            strip_background=element_rect(fill="#333333", color="none"),
            strip_text_x=element_text(color="white"),
            strip_text_y=element_text(color="white", angle=-90),
        )

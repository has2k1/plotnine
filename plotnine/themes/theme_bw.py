from .elements import element_line, element_rect, element_text
from .theme import theme
from .theme_gray import theme_gray


class theme_bw(theme_gray):
    """
    White background with black gridlines

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
            axis_text=element_text(size=0.8 * base_size),
            panel_background=element_rect(fill="white"),
            panel_border=element_rect(fill="none", color="#7f7f7f"),
            panel_grid_major=element_line(color="#E5E5E5"),
            panel_grid_minor=element_line(color="#FAFAFA"),
            strip_background=element_rect(
                fill="#CCCCCC", color="#7F7F7F", size=1
            ),
        )

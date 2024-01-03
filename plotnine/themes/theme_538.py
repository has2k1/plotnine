from .elements import element_blank, element_line, element_rect, element_text
from .theme import theme
from .theme_gray import theme_gray


class theme_538(theme_gray):
    """
    Theme in the likeness of fivethirtyeight.com plots

    Parameters
    ----------
    base_size : int
        Base font size. All text sizes are a scaled versions of
        the base font size.
    base_family : str
        Base font family.
    """

    def __init__(self, base_size=11, base_family="DejaVu Sans"):
        super().__init__(base_size, base_family)
        bgcolor = "#F0F0F0"
        self += theme(
            axis_ticks=element_blank(),
            title=element_text(color="#3C3C3C"),
            legend_background=element_rect(fill="None"),
            legend_key=element_rect(fill="#E0E0E0"),
            panel_background=element_rect(fill=bgcolor),
            panel_border=element_blank(),
            panel_grid_major=element_line(
                color="#D5D5D5", linetype="solid", size=1
            ),
            panel_grid_minor=element_blank(),
            plot_background=element_rect(fill=bgcolor, color=bgcolor, size=1),
            strip_background=element_rect(size=0),
        )

from .elements import (element_line, element_rect,
                       element_text, element_blank)
from .theme import theme
from .theme_gray import theme_gray


class theme_538(theme_gray):
    """
    Theme in the likeness of fivethirtyeight.com plots

    Parameters
    ----------
    base_size : int, optional
        Base font size. All text sizes are a scaled versions of
        the base font size. Default is 11.
    base_family : str, optional
        Base font family.
    """
    def __init__(self, base_size=11, base_family='DejaVu Sans'):
        theme_gray.__init__(self, base_size, base_family)
        bgcolor = '#F0F0F0'
        self.add_theme(
            theme(
                axis_ticks=element_blank(),
                title=element_text(color='#3C3C3C'),
                legend_background=element_rect(fill='None'),
                legend_key=element_rect(fill='#E0E0E0'),
                panel_background=element_rect(fill=bgcolor),
                panel_border=element_blank(),
                panel_grid_major=element_line(
                    color='#D5D5D5', linetype='solid', size=1),
                panel_grid_minor=element_blank(),
                plot_background=element_rect(
                    fill=bgcolor, color=bgcolor, size=1),
                strip_background=element_rect(size=0)),
            inplace=True)

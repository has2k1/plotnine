from .elements import element_line, element_rect, element_blank
from .theme import theme
from .theme_bw import theme_bw


class theme_classic(theme_bw):
    """
    A classic-looking theme, with x & y axis lines and
    no gridlines.

    Parameters
    ----------
    base_size : int, optional
        Base font size. All text sizes are a scaled versions of
        the base font size. Default is 11.
    base_family : str, optional
        Base font family.
    """

    def __init__(self, base_size=11, base_family='DejaVu Sans'):
        theme_bw.__init__(self, base_size, base_family)
        self.add_theme(
            theme(panel_border=element_blank(),
                  axis_line=element_line(color='black'),
                  panel_grid_major=element_line(),
                  panel_grid_major_x=element_blank(),
                  panel_grid_major_y=element_blank(),
                  panel_grid_minor=element_line(),
                  panel_grid_minor_x=element_blank(),
                  panel_grid_minor_y=element_blank(),
                  strip_background=element_rect(
                      colour='black', fill='None', size=1),
                  legend_key=element_blank()),
            inplace=True)

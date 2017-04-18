from .elements import element_line, element_rect, element_text
from .theme import theme
from .theme_gray import theme_gray


class theme_linedraw(theme_gray):
    """
    A theme with only black lines of various widths on white backgrounds

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
        self.add_theme(theme(
            axis_text=element_text(color='black', size=base_size*0.8),
            axis_ticks=element_line(color='black', size=0.5),
            legend_key=element_rect(color='black', size=0.5),
            panel_background=element_rect(fill='white'),
            panel_border=element_rect(fill='None', color='black', size=1),
            panel_grid_major=element_line(color='black', size=0.1),
            panel_grid_minor=element_line(color='black', size=0.02),
            strip_background=element_rect(
                fill='black', color='black', size=1),
            strip_text_x=element_text(color='white'),
            strip_text_y=element_text(color='white', angle=-90)
        ), inplace=True)

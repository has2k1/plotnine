from .elements import element_line, element_rect, element_text
from .theme import theme
from .theme_gray import theme_gray


class theme_linedraw(theme_gray):
    """
    A theme with only black lines of various widths on white backgrounds
    """

    def __init__(self, base_size=12, base_family='sans-serif'):
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
            strip_text_y=element_text(color='white', angle=90)
        ), inplace=True)

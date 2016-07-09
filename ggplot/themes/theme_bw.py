from .elements import element_line, element_rect, element_text
from .theme import theme
from .theme_gray import theme_gray


class theme_bw(theme_gray):
    """
    White background with black gridlines
    """

    def __init__(self, base_size=12, base_family='sans-serif'):
        theme_gray.__init__(self, base_size, base_family)
        self.add_theme(
            theme(axis_text=element_text(size=0.8*base_size),
                  axis_ticks=element_line(color='black'),
                  legend_key=element_rect(color='#CCCCCC'),
                  panel_background=element_rect(
                      fill='white', color='None'),
                  panel_border=element_rect(
                      fill='None', color='#7f7f7f'),
                  panel_grid_major=element_line(
                      color='#E5E5E5', size=0.8),
                  panel_grid_minor=element_line(
                      color='#FAFAFA', size=1),
                  strip_background=element_rect(
                      fill='#CCCCCC', color='#7F7F7F', size=0.2)),
            inplace=True)

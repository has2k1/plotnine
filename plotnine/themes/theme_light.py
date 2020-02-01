from .elements import element_line, element_rect, element_text, element_blank
from .theme import theme
from .theme_gray import theme_gray


class theme_light(theme_gray):
    """
    A theme similar to :class:`theme_linedraw` but with light grey
    lines and axes to direct more attention towards the data.

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
            axis_ticks=element_line(color='#B3B3B3', size=0.5),
            axis_ticks_minor=element_blank(),
            legend_key=element_rect(fill='white', color='#7F7F7F', size=0.5),
            panel_background=element_rect(fill='white'),
            panel_border=element_rect(fill='None', color='#B3B3B3', size=1),
            panel_grid_major=element_line(color='#D9D9D9', size=0.5),
            panel_grid_minor=element_line(color='#EDEDED', size=0.25),
            strip_background=element_rect(
                fill='#B3B3B3', color='#B3B3B3', size=1),
            strip_text_x=element_text(color='white'),
            strip_text_y=element_text(color='white', angle=-90)
        ), inplace=True)

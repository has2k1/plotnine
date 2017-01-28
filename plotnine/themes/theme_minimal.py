from .elements import element_blank
from .theme import theme
from .theme_bw import theme_bw


class theme_minimal(theme_bw):
    """
    A minimalistic theme with no background annotations
    """

    def __init__(self, base_size=12, base_family='sans-serif'):
        theme_bw.__init__(self, base_size, base_family)
        self.add_theme(
            theme(legend_background=element_blank(),
                  legend_key=element_blank(),
                  panel_background=element_blank(),
                  panel_border=element_blank(),
                  strip_background=element_blank(),
                  plot_background=element_blank(),
                  axis_ticks=element_blank(),
                  axis_ticks_length=12),
            inplace=True)

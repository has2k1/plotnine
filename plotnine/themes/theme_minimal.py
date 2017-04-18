from .elements import element_blank
from .theme import theme
from .theme_bw import theme_bw


class theme_minimal(theme_bw):
    """
    A minimalistic theme with no background annotations

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
            theme(legend_background=element_blank(),
                  legend_key=element_blank(),
                  panel_background=element_blank(),
                  panel_border=element_blank(),
                  strip_background=element_blank(),
                  plot_background=element_blank(),
                  axis_ticks=element_blank(),
                  axis_ticks_length=12),
            inplace=True)

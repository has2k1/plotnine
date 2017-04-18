from ..options import get_option
from .elements import element_text, element_blank
from .theme import theme


class theme_void(theme):
    """
    A classic-looking theme, with x & y axis lines and
    no gridlines.

    Parameters
    ----------
    base_size : int, optional
        Base font size. All text sizes are a scaled versions of
        the base font size. Default is 11.
    base_family : int, optional
        Base font family.
    """

    def __init__(self, base_size=11, base_family='DejaVu Sans'):
        # Use only inherited elements and make everything blank
        theme.__init__(
            self,
            line=element_blank(),
            rect=element_blank(),
            text=element_text(
                family=base_family, style='normal', color='black',
                size=base_size, linespacing=0.9, ha='center',
                va='center', rotation=0),
            aspect_ratio=get_option('aspect_ratio'),
            dpi=get_option('dpi'),
            figure_size=get_option('figure_size'),
            plot_margin=None,
            panel_spacing=0,
            axis_text_x=element_blank(),
            axis_text_y=element_blank(),
            axis_title_x=element_blank(),
            axis_title_y=element_blank(),
            legend_entry_spacing_x=5,
            legend_entry_spacing_y=2,
            legend_text=element_text(size=base_size*0.8, ha='left'),
            legend_text_legend=element_text(va='baseline'),
            legend_title=element_text(ha='left'),
            strip_text=element_text(
                size=base_size*0.8, linespacing=1.8),

            complete=True)

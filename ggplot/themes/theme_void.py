from .elements import element_text, element_blank
from .theme import theme


class theme_void(theme):
    """
    A classic-looking theme, with x & y axis lines and
    no gridlines.
    """

    def __init__(self, base_size=12, base_family='sans-serif'):
        # Use only inherited elements and make everything blank
        theme.__init__(
            self,
            line=element_blank(),
            rect=element_blank(),
            text=element_text(
                family=base_family, style='normal', color='black',
                size=base_size, linespacing=0.9, ha='center',
                va='center', rotaion=0),
            figure_size=(11, 8),
            plot_margin=None,
            axis_text_x=element_blank(),
            axis_text_y=element_blank(),
            axis_title_x=element_blank(),
            axis_title_y=element_blank(),
            legend_text=element_text(
                size=base_size*0.8, ha='left', va='baseline'),
            legend_title=element_blank(),
            strip_text=element_text(
                size=base_size*0.8, linespacing=1.8),

            complete=True)

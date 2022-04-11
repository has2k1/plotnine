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

    def __init__(self, base_size=11, base_family=None):
        base_family = base_family or get_option('base_family')
        half_line = base_size/2
        # Use only inherited elements and make everything blank
        theme.__init__(
            self,
            line=element_blank(),
            rect=element_blank(),
            text=element_text(
                family=base_family,
                style='normal',
                color='black',
                size=base_size,
                linespacing=0.9,
                ha='center',
                va='center',
                rotation=0,
                margin={}
            ),
            aspect_ratio=get_option('aspect_ratio'),
            dpi=get_option('dpi'),
            figure_size=get_option('figure_size'),
            axis_text_x=element_blank(),
            axis_text_y=element_blank(),
            axis_title_x=element_blank(),
            axis_title_y=element_blank(),
            legend_box='auto',
            legend_box_just='auto',
            legend_box_margin=10,
            legend_box_spacing=0.1,
            legend_direction='auto',
            legend_entry_spacing_x=5,
            legend_entry_spacing_y=2,
            legend_key_height=18,
            legend_key_width=18,
            legend_margin=10,
            legend_position='right',
            legend_spacing=10,
            legend_text=element_text(
                size=base_size*0.8,
                ha='left',
                margin={'t': 3, 'b': 3, 'l': 3, 'r': 3, 'units': 'pt'}
            ),
            legend_text_legend=element_text(va='baseline'),
            legend_title=element_text(ha='left', margin={'b': 8}),
            legend_title_align='auto',
            plot_margin=None,
            plot_title=element_text(
                margin={'b': half_line*1.2, 'units': 'pt'}
            ),
            panel_spacing=0,
            plot_caption=element_text(
                margin={'t': 7.2, 'r': 0, 'units': 'pt'}
            ),
            strip_margin=0,
            strip_text=element_text(
                size=base_size*0.8,
                linespacing=1.8,
                margin={'t': 3, 'b': 3, 'l': 3, 'r': 3, 'units': 'pt'}
            ),

            complete=True
        )

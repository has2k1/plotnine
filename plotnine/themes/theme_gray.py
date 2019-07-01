from ..options import get_option
from ..utils import alias
from .elements import (element_line, element_rect,
                       element_text, element_blank)
from .theme import theme


class theme_gray(theme):
    """
    A gray background with white gridlines.

    This is the default theme

    Parameters
    ----------
    base_size : int, optional
        Base font size. All text sizes are a scaled versions of
        the base font size. Default is 11.
    base_family : str, optional
        Base font family.
    """
    def __init__(self, base_size=11, base_family='DejaVu Sans'):
        half_line = base_size/2
        # super does not work well with reloads
        theme.__init__(
            self,
            line=element_line(color='black', size=1,
                              linetype='solid', lineend='butt'),
            rect=element_rect(fill='white', color='black',
                              size=1, linetype='solid'),
            text=element_text(family=base_family, style='normal',
                              color='black', size=base_size,
                              linespacing=0.9, ha='center',
                              va='center', rotation=0, margin={}),
            aspect_ratio=get_option('aspect_ratio'),

            axis_line=element_line(),
            axis_line_x=element_blank(),
            axis_line_y=element_blank(),
            axis_text=element_text(size=base_size*.8,
                                   color='#4D4D4D'),
            axis_text_x=element_text(
                va='top', margin={'t': half_line*0.8/2}),
            axis_text_y=element_text(
                ha='right', margin={'r': half_line*0.8/2}),
            axis_ticks=element_line(color='#333333'),
            axis_ticks_length=0,
            axis_ticks_length_major=half_line/2,
            axis_ticks_length_minor=half_line/4,
            axis_ticks_minor=element_blank(),
            axis_ticks_direction='out',
            axis_ticks_pad=2,
            axis_title_x=element_text(
                va='top', margin={'t': half_line*0.8}),
            axis_title_y=element_text(
                angle=90, va='bottom', margin={'r': half_line*0.8}),

            dpi=get_option('dpi'),
            figure_size=get_option('figure_size'),

            # legend, None values are for parameters where the
            # drawing routines can make better decisions than
            # can be pre-determined in the theme.
            legend_background=element_rect(color='None'),
            legend_entry_spacing_x=5,
            legend_entry_spacing_y=2,
            legend_key=element_rect(fill='#F2F2F2',
                                    colour='None'),
            legend_key_size=base_size*0.8*1.8,
            legend_key_height=None,
            legend_key_width=None,
            legend_margin=0,     # points
            legend_spacing=10,   # points
            legend_text=element_text(
                size=base_size*0.8, ha='left',
                margin={'t': 3, 'b': 3, 'l': 3, 'r': 3,
                        'units': 'pt'}),
            legend_text_legend=element_text(va='baseline'),
            legend_text_colorbar=element_text(va='center'),
            legend_title=element_text(ha='left',
                                      margin={'t': half_line*0.8,
                                              'b': half_line*0.8,
                                              'l': half_line*0.8,
                                              'r': half_line*0.8,
                                              'units': 'pt'}),
            legend_title_align=None,
            legend_position='right',
            legend_box=None,
            legend_box_margin=10,    # points
            legend_box_just=None,
            legend_box_spacing=0.1,  # In inches
            legend_direction=None,

            panel_background=element_rect(fill='#EBEBEB'),
            panel_border=element_blank(),
            panel_grid_major=element_line(color='white', size=1),
            panel_grid_minor=element_line(color='white', size=0.5),
            panel_spacing=0.07,
            panel_spacing_x=0.07,
            panel_spacing_y=0.07,
            panel_ontop=True,

            strip_background=element_rect(fill='#D9D9D9', color='None'),
            strip_margin=0,
            strip_margin_x=None,
            strip_margin_y=None,
            strip_text=element_text(color='#1A1A1A', size=base_size*0.8,
                                    linespacing=1.0),
            strip_text_x=element_text(
                margin={'t': half_line/2, 'b': half_line/2}),
            strip_text_y=element_text(
                margin={'l': half_line/2, 'r': half_line/2},
                rotation=-90),

            plot_background=element_rect(color='white'),
            plot_title=element_text(size=base_size*1.2,
                                    margin={'b': half_line*1.2,
                                            'units': 'pt'}),
            plot_margin=None,

            complete=True)


alias('theme_grey', theme_gray)

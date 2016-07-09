from __future__ import division

from .elements import (element_line, element_rect,
                       element_text, element_blank)
from .theme import theme


class theme_gray(theme):
    """
    A gray background with white gridlines.

    This is the default theme
    """
    def __init__(self, base_size=11, base_family='sans-serif'):
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
                              va='center', rotation=0),

            axis_line=element_line(),
            axis_line_x=element_blank(),
            axis_line_y=element_blank(),
            axis_text=element_text(size=base_size*.8,
                                   color='#4D4D4D'),
            axis_text_x=element_text(va='top'),
            axis_text_y=element_text(ha='right'),
            axis_ticks=element_line(color='#333333'),
            axis_ticks_length=0,
            axis_ticks_major_length=half_line/2,
            axis_ticks_minor_length=0,
            axis_ticks_direction='out',
            axis_ticks_pad=2,
            axis_title_x=element_text(),
            axis_title_y=element_text(angle=90),

            dpi=300,
            figure_size=(11, 8),

            legend_background=element_rect(color='None'),
            legend_margin=0.2,    # covert cm -> pixels
            legend_key=element_rect(fill='#F2F2F2',
                                    colour='white'),
            legend_key_size=1.2,  # convert lines -> pixels
            legend_key_height=None,
            legend_key_width=None,
            legend_text=element_text(size=base_size*0.8,
                                     ha='left', va='baseline'),
            legend_text_align=None,
            legend_title=element_text(ha='left'),
            legend_title_align=None,
            legend_position='right',
            legend_direction=None,
            legend_justification='center',
            legend_box=None,

            panel_background=element_rect(fill='#EBEBEB', color='None'),
            panel_border=element_blank(),
            panel_grid_major=element_line(color='white', size=1),
            panel_grid_minor=element_line(color='white', size=0.5),
            panel_margin=None,
            panel_margin_x=None,
            panel_margin_y=None,
            panel_ontop=True,

            strip_background=element_rect(fill='#D9D9D9', color='None'),
            strip_text=element_text(color='#1A1A1A', size=base_size*0.8,
                                    linespacing=2),
            strip_text_x=element_text(),
            strip_text_y=element_text(rotation=-90),

            plot_background=element_rect(color='white'),
            plot_title=element_text(size=base_size*1.2),
            plot_margin=None,

            complete=True)

        d = {
            'axes.axisbelow': 'True',
            'font.sans-serif': ['Helvetica', 'Avant Garde',
                                'Computer Modern Sans serif', 'Arial'],
            'font.serif': ['Times', 'Palatino',
                           'New Century Schoolbook', 'Bookman',
                           'Computer Modern Roman', 'Times New Roman'],
            'lines.antialiased': 'True',
            'patch.antialiased': 'True',
            'timezone': 'UTC',
        }

        self._rcParams.update(d)


theme_grey = theme_gray()

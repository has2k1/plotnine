from ..options import get_option
from .theme import theme
from .elements import element_text
from .seaborn_rcmod import set_theme


class theme_seaborn(theme):
    """
    Theme for seaborn.

    Credit to Michael Waskom's seaborn:

        - http://stanford.edu/~mwaskom/software/seaborn
        - https://github.com/mwaskom/seaborn

    Parameters
    ----------
    style: str in ``['whitegrid', 'darkgrid', 'nogrid', 'ticks']``
        Style of axis background.
    context: str in ``['notebook', 'talk', 'paper', 'poster']``
        Intended context for resulting figures.
    font : str
        Font family, see matplotlib font manager.
    font_scale : float, optional
        Separate scaling factor to independently scale the
        size of the font elements.
    """

    def __init__(self, style='darkgrid', context='notebook',
                 font='sans-serif', font_scale=1):
        theme.__init__(
            self,
            aspect_ratio=get_option('aspect_ratio'),
            dpi=get_option('dpi'),
            figure_size=get_option('figure_size'),
            panel_spacing=0.1,

            legend_box='auto',
            legend_box_just='auto',
            legend_box_margin=10,
            legend_direction='auto',
            legend_entry_spacing_x=5,
            legend_entry_spacing_y=2,
            legend_key_height=18,
            legend_key_width=18,
            legend_margin=10,
            legend_spacing=10,
            legend_text=element_text(
                va='baseline',
                ha='left',
                margin={'t': 3, 'b': 3, 'l': 3, 'r': 3, 'units': 'pt'}
            ),
            legend_title=element_text(margin={'b': 8}),
            legend_title_align='auto',
            legend_position='right',
            strip_text=element_text(
                margin={'t': 3, 'b': 3, 'l': 3, 'r': 3, 'units': 'pt'}
            ),

            complete=True
        )

        d = set_theme(
            context=context,
            style=style,
            font=font,
            font_scale=font_scale
        )

        self._rcParams.update(d)

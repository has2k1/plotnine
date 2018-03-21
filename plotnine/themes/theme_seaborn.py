from ..options import get_option
from .theme import theme
from .seaborn_rcmod import set as seaborn_set


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
        theme.__init__(self,
                       aspect_ratio=get_option('aspect_ratio'),
                       dpi=get_option('dpi'),
                       figure_size=get_option('figure_size'),
                       panel_spacing=0.1,
                       complete=True)
        d = seaborn_set(context=context, style=style,
                        font=font, font_scale=font_scale)
        self._rcParams.update(d)

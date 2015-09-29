from .theme import theme
from .seaborn_rcmod import set as seaborn_set


class theme_seaborn(theme):
    """
    Theme for seaborn.

    Copied from mwaskom's seaborn:
        https://github.com/mwaskom/seaborn/blob/master/seaborn/rcmod.py

    Parameters
    ----------
    style: whitegrid | darkgrid | nogrid | ticks
        Style of axis background.
    context: notebook | talk | paper | poster
        Intended context for resulting figures.
    gridweight: extra heavy | heavy | medium | light
        Width of the grid lines. None
    """

    def __init__(self, style='darkgrid', context='notebook',
                 font='sans-serif', font_scale=1):
        theme.__init__(self, complete=True)
        d = seaborn_set(context=context, style=style,
                        font=font, font_scale=font_scale)
        self._rcParams.update(d)

        d = {
             'figure.figsize': '11, 8',
             'figure.subplot.hspace': '0.5'}
        self._rcParams.update(d)

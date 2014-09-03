import matplotlib as mpl

from .theme_gray import theme_gray


class theme_bw(theme_gray):
    """
    White background w/ black gridlines
    """

    def __init__(self):
        super(theme_bw, self).__init__()
        self._rcParams['axes.facecolor'] = 'white'
        self._rcParams["grid.linewidth"] = "0.5"
        self._rcParams["grid.color"] = "#E5E5E5"
        self._rcParams["xtick.color"] = "black"
        self._rcParams["ytick.color"] = "black"

    def apply_theme(self, ax, params):
        """
        Styles x,y axes to appear like ggplot2
        Must be called after all plot and axis manipulation operations have
        been carried out (needs to know final tick spacing)

        From:
        https://github.com/wrobstory/climatic/blob/master/climatic/stylers.py
        """
        # Restyle the tick lines
        for line in ax.get_xticklines() + ax.get_yticklines():
            line.set_markersize(5)
            line.set_markeredgewidth(mpl.rcParams['grid.linewidth'])

        # set parameters
        for att, val in params['xaxis']:
            getattr(ax.xaxis, att)(val)

        for att, val in params['yaxis']:
            getattr(ax.yaxis, att)(val)

        # Set minor grid lines
        ax.grid(True, 'minor', color='#FAFAFA', linestyle='-', linewidth=0.5)

        if not isinstance(ax.xaxis.get_major_locator(), mpl.ticker.LogLocator):
            ax.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator(2))
        if not isinstance(ax.yaxis.get_major_locator(), mpl.ticker.LogLocator):
            ax.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator(2))

from .theme import theme

import matplotlib as mpl
import matplotlib.pyplot as plt
from numpy import isreal


class theme_538(theme):
    """
    Theme for 538.

    Copied from CamDavidsonPilon's gist:
        https://gist.github.com/CamDavidsonPilon/5238b6499b14604367ac

   """

    def __init__(self):
        super(theme_538, self).__init__(complete=True)
        self._rcParams["lines.linewidth"] = "2.0"
        self._rcParams["examples.download"] = "True"
        self._rcParams["patch.linewidth"] = "0.5"
        self._rcParams["legend.fancybox"] = "True"
        self._rcParams["axes.color_cycle"] = [ "#30a2da", "#fc4f30", "#e5ae38",
                                               "#6d904f", "#8b8b8b"]
        self._rcParams["axes.facecolor"] = "#f0f0f0"
        self._rcParams["axes.labelsize"] = "large"
        self._rcParams["axes.axisbelow"] = "True"
        self._rcParams["axes.grid"] = "True"
        self._rcParams["patch.edgecolor"] = "#f0f0f0"
        self._rcParams["axes.titlesize"] = "x-large"
        self._rcParams["svg.embed_char_paths"] = "path"
        self._rcParams["examples.directory"] = ""
        self._rcParams["figure.facecolor"] = "#f0f0f0"
        self._rcParams["grid.linestyle"] = "-"
        self._rcParams["grid.linewidth"] = "1.0"
        self._rcParams["grid.color"] = "#cbcbcb"
        self._rcParams["axes.edgecolor"] = "#f0f0f0"
        self._rcParams["xtick.major.size"] = "0"
        self._rcParams["xtick.minor.size"] = "0"
        self._rcParams["ytick.major.size"] = "0"
        self._rcParams["ytick.minor.size"] = "0"
        self._rcParams["axes.linewidth"] = "3.0"
        self._rcParams["font.size"] ="14.0"
        self._rcParams["lines.linewidth"] = "4"
        self._rcParams["lines.solid_capstyle"] = "butt"
        self._rcParams["savefig.edgecolor"] = "#f0f0f0"
        self._rcParams["savefig.facecolor"] = "#f0f0f0"
        self._rcParams["figure.subplot.left"]   = "0.08"
        self._rcParams["figure.subplot.right"]  = "0.95"
        self._rcParams["figure.subplot.bottom"] = "0.07"


    def apply_theme(self, ax):
        '''Styles x,y axes to appear like ggplot2
        Must be called after all plot and axis manipulation operations have
        been carried out (needs to know final tick spacing)

        From: https://github.com/wrobstory/climatic/blob/master/climatic/stylers.py
        '''
        #Remove axis border
        for child in ax.get_children():
            if isinstance(child, mpl.spines.Spine):
                child.set_alpha(0)

        #Restyle the tick lines
        for line in ax.get_xticklines() + ax.get_yticklines():
            line.set_markersize(5)
            line.set_markeredgewidth(1.4)

        #Only show bottom left ticks
        ax.xaxis.set_ticks_position('bottom')
        ax.yaxis.set_ticks_position('left')

        #Set minor grid lines
        ax.grid(True, 'minor', color='#F2F2F2', linestyle='-', linewidth=0.7)

        if not isinstance(ax.xaxis.get_major_locator(), mpl.ticker.LogLocator):
            ax.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator(2))
        if not isinstance(ax.yaxis.get_major_locator(), mpl.ticker.LogLocator):
            ax.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator(2))


from .theme import theme
from .element_text import element_text

import matplotlib as mpl


class theme_gray(theme):
    """
    Standard theme for ggplot. Gray background w/ white gridlines.

    Copied from the the ggplot2 codebase:
        https://github.com/hadley/ggplot2/blob/master/R/theme-defaults.r
    """
    def __init__(self):
        # super does not work well with reloads
        theme.__init__(self, complete=True)
        self._rcParams["timezone"] = "UTC"
        self._rcParams["lines.linewidth"] = "1.0"
        self._rcParams["lines.antialiased"] = "True"
        self._rcParams["patch.linewidth"] = "0.5"
        self._rcParams["patch.facecolor"] = "348ABD"
        self._rcParams["patch.edgecolor"] = "#E5E5E5"
        self._rcParams["patch.antialiased"] = "True"
        self._rcParams["font.family"] = "sans-serif"
        self._rcParams["font.size"] = "12.0"
        self._rcParams["font.serif"] = ["Times", "Palatino",
                                        "New Century Schoolbook",
                                        "Bookman", "Computer Modern Roman",
                                        "Times New Roman"]
        self._rcParams["font.sans-serif"] = ["Helvetica", "Avant Garde",
                                             "Computer Modern Sans serif",
                                             "Arial"]
        self._rcParams["axes.facecolor"] = "#E5E5E5"
        self._rcParams["axes.edgecolor"] = "bcbcbc"
        self._rcParams["axes.linewidth"] = "1"
        self._rcParams["axes.grid"] = "True"
        self._rcParams["axes.titlesize"] = "x-large"
        self._rcParams["axes.labelsize"] = "large"
        self._rcParams["axes.labelcolor"] = "black"
        self._rcParams["axes.axisbelow"] = "True"
        self._rcParams["axes.color_cycle"] = ["#333333", "348ABD", "7A68A6",
                                              "A60628",
                                              "467821", "CF4457", "188487",
                                              "E24A33"]
        self._rcParams["grid.color"] = "white"
        self._rcParams["grid.linewidth"] = "1.2"
        self._rcParams["grid.linestyle"] = "solid"
        self._rcParams["xtick.major.size"] = "0"
        self._rcParams["xtick.minor.size"] = "0"
        self._rcParams["xtick.major.pad"] = "6"
        self._rcParams["xtick.minor.pad"] = "6"
        self._rcParams["xtick.color"] = "#7F7F7F"
        self._rcParams["xtick.direction"] = "out"  # pointing out of axis
        self._rcParams["ytick.major.size"] = "0"
        self._rcParams["ytick.minor.size"] = "0"
        self._rcParams["ytick.major.pad"] = "6"
        self._rcParams["ytick.minor.pad"] = "6"
        self._rcParams["ytick.color"] = "#7F7F7F"
        self._rcParams["ytick.direction"] = "out"  # pointing out of axis

        self._rcParams["legend.fancybox"] = "True"
        self._rcParams["figure.figsize"] = "11, 8"
        self._rcParams["figure.facecolor"] = "1.0"
        self._rcParams["figure.edgecolor"] = "0.50"
        self._rcParams["figure.subplot.hspace"] = "0.5"

    def apply_theme(self, ax, params):
        """
        Styles x,y axes to appear like ggplot2
        Must be called after all plot and axis manipulation operations have
        been carried out (needs to know final tick spacing)

        From:
        https://github.com/wrobstory/climatic/blob/master/climatic/stylers.py
        """
        # Remove axis border
        for child in ax.get_children():
            if isinstance(child, mpl.spines.Spine):
                child.set_alpha(0)
                child.set_linewidth(0)

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
        ax.grid(True, 'minor', color='#F2F2F2', linestyle='-', linewidth=0.5)

        if not isinstance(ax.xaxis.get_major_locator(), mpl.ticker.LogLocator):
            ax.xaxis.set_minor_locator(mpl.ticker.AutoMinorLocator(2))
        if not isinstance(ax.yaxis.get_major_locator(), mpl.ticker.LogLocator):
            ax.yaxis.set_minor_locator(mpl.ticker.AutoMinorLocator(2))

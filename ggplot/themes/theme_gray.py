from .theme import theme

import matplotlib as mpl


def _set_default_theme_rcparams(rcParams):
    """helper method to set the default rcParams and other theming relevant
    things
    """
    rcParams["timezone"] = "UTC"
    rcParams["lines.linewidth"] = "1.0"
    rcParams["lines.antialiased"] = "True"
    rcParams["patch.linewidth"] = "0.5"
    rcParams["patch.facecolor"] = "348ABD"
    rcParams["patch.edgecolor"] = "#E5E5E5"
    rcParams["patch.antialiased"] = "True"
    rcParams["font.family"] = "sans-serif"
    rcParams["font.size"] = "12.0"
    rcParams["font.serif"] = ["Times", "Palatino", "New Century Schoolbook",
                              "Bookman", "Computer Modern Roman",
                              "Times New Roman"]
    rcParams["font.sans-serif"] = ["Helvetica", "Avant Garde",
                                   "Computer Modern Sans serif", "Arial"]
    rcParams["axes.facecolor"] = "#E5E5E5"
    rcParams["axes.edgecolor"] = "bcbcbc"
    rcParams["axes.linewidth"] = "1"
    rcParams["axes.grid"] = "True"
    rcParams["axes.titlesize"] = "x-large"
    rcParams["axes.labelsize"] = "large"
    rcParams["axes.labelcolor"] = "black"
    rcParams["axes.axisbelow"] = "True"
    rcParams["axes.color_cycle"] = ["#333333", "348ABD", "7A68A6", "A60628",
                                    "467821", "CF4457", "188487", "E24A33"]
    rcParams["grid.color"] = "white"
    rcParams["grid.linewidth"] = "1.4"
    rcParams["grid.linestyle"] = "solid"
    rcParams["xtick.major.size"] = "0"
    rcParams["xtick.minor.size"] = "0"
    rcParams["xtick.major.pad"] = "6"
    rcParams["xtick.minor.pad"] = "6"
    rcParams["xtick.color"] = "#7F7F7F"
    rcParams["xtick.direction"] = "out"  # pointing out of axis
    rcParams["ytick.major.size"] = "0"
    rcParams["ytick.minor.size"] = "0"
    rcParams["ytick.major.pad"] = "6"
    rcParams["ytick.minor.pad"] = "6"
    rcParams["ytick.color"] = "#7F7F7F"
    rcParams["ytick.direction"] = "out"  # pointing out of axis
    rcParams["legend.fancybox"] = "True"
    rcParams["figure.figsize"] = "11, 8"
    rcParams["figure.facecolor"] = "1.0"
    rcParams["figure.edgecolor"] = "0.50"
    rcParams["figure.subplot.hspace"] = "0.5"


class theme_gray(theme):
    """
    Standard theme for ggplot. Gray background w/ white gridlines.

    Copied from the the ggplot2 codebase:
        https://github.com/hadley/ggplot2/blob/master/R/theme-defaults.r
    """
    def __init__(self):
        super(theme_gray, self).__init__(complete=True)

    def apply_rcparams(self, rcParams):
        _set_default_theme_rcparams(rcParams)
        super(theme_gray, self).apply_rcparams(rcParams)

    def apply_theme(self, gg):
        _theme_grey_post_plot_callback(gg)

def _theme_grey_post_plot_callback(ax):
    '''Styles x,y axes to appear like ggplot2
    Must be called after all plot and axis manipulation operations have been
    carried out (needs to know final tick spacing)

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

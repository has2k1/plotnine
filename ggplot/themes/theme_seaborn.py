from .theme import theme

import matplotlib as mpl
import matplotlib.pyplot as plt
from numpy import isreal

def _set_default_theme_rcparams(gg, style, gridweight, context):
    """helper method to set the default rcParams and other theming relevant
    things
    """
    # select grid line width:
    gridweights = {
        'extra heavy': 1.5,
        'heavy': 1.1,
        'medium': 0.8,
        'light': 0.5,
    }
    if gridweight is None:
        if context == "paper":
            glw = gridweights["medium"]
        else:
            glw = gridweights['extra heavy']
    elif isreal(gridweight):
        glw = gridweight
    else:
        glw = gridweights[gridweight]

    if style == "darkgrid":
        lw = .8 if context == "paper" else 1.5
        ax_params = {"axes.facecolor": "#EAEAF2",
                     "axes.edgecolor": "white",
                     "axes.linewidth": 0,
                     "axes.grid": True,
                     "axes.axisbelow": True,
                     "grid.color": "w",
                     "grid.linestyle": "-",
                     "grid.linewidth": glw}

    elif style == "whitegrid":
        lw = 1.0 if context == "paper" else 1.7
        ax_params = {"axes.facecolor": "white",
                     "axes.edgecolor": "#CCCCCC",
                     "axes.linewidth": lw,
                     "axes.grid": True,
                     "axes.axisbelow": True,
                     "grid.color": "#DDDDDD",
                     "grid.linestyle": "-",
                     "grid.linewidth": glw}

    elif style == "nogrid":
        ax_params = {"axes.grid": False,
                     "axes.facecolor": "white",
                     "axes.edgecolor": "black",
                     "axes.linewidth": 1}

    elif style == "ticks":
        ticksize = 3. if context == "paper" else 6.
        tickwidth = .5 if context == "paper" else 1
        ax_params = {"axes.grid": False,
                     "axes.facecolor": "white",
                     "axes.edgecolor": "black",
                     "axes.linewidth": 1,
                     "xtick.direction": "out",
                     "ytick.direction": "out",
                     "xtick.major.width": tickwidth,
                     "ytick.major.width": tickwidth,
                     "xtick.minor.width": tickwidth,
                     "xtick.minor.width": tickwidth,
                     "xtick.major.size": ticksize,
                     "xtick.minor.size": ticksize / 2,
                     "ytick.major.size": ticksize,
                     "ytick.minor.size": ticksize / 2}

    gg.rcParams.update(ax_params)

    # Determine the font sizes
    if context == "talk":
        font_params = {"axes.labelsize": 16,
                       "axes.titlesize": 19,
                       "xtick.labelsize": 14,
                       "ytick.labelsize": 14,
                       "legend.fontsize": 13,
                       }

    elif context == "notebook":
        font_params = {"axes.labelsize": 11,
                       "axes.titlesize": 12,
                       "xtick.labelsize": 10,
                       "ytick.labelsize": 10,
                       "legend.fontsize": 10,
                       }

    elif context == "poster":
        font_params = {"axes.labelsize": 18,
                       "axes.titlesize": 22,
                       "xtick.labelsize": 16,
                       "ytick.labelsize": 16,
                       "legend.fontsize": 16,
                       }

    elif context == "paper":
        font_params = {"axes.labelsize": 8,
                       "axes.titlesize": 12,
                       "xtick.labelsize": 8,
                       "ytick.labelsize": 8,
                       "legend.fontsize": 8,
                       }

    gg.rcParams.update(font_params)

    # Set other parameters
    gg.rcParams.update({
        "lines.linewidth": 1.1 if context == "paper" else 1.4,
        "patch.linewidth": .1 if context == "paper" else .3,
        "xtick.major.pad": 3.5 if context == "paper" else 7,
        "ytick.major.pad": 3.5 if context == "paper" else 7,
        })

    # # Set the constant defaults
    # mpl.rc("font", family=font)
    # mpl.rc("legend", frameon=False, numpoints=1)
    # mpl.rc("lines", markeredgewidth=0, solid_capstyle="round")
    # mpl.rc("figure", figsize=(8, 5.5))
    # mpl.rc("image", cmap="cubehelix")


    gg.rcParams["timezone"] = "UTC"
    # gg.rcParams["lines.linewidth"] = "1.0"
    # gg.rcParams["lines.antialiased"] = "True"
    # gg.rcParams["patch.linewidth"] = "0.5"
    # gg.rcParams["patch.facecolor"] = "348ABD"
    # gg.rcParams["patch.edgecolor"] = "#E5E5E5"
    gg.rcParams["patch.antialiased"] = "True"
    gg.rcParams["font.family"] = "sans-serif"
    gg.rcParams["font.size"] = "12.0"
    gg.rcParams["font.serif"] = ["Times", "Palatino", "New Century Schoolbook",
            "Bookman", "Computer Modern Roman",
            "Times New Roman"]
    gg.rcParams["font.sans-serif"] = ["Helvetica", "Avant Garde",
            "Computer Modern Sans serif", "Arial"]
    # gg.rcParams["axes.facecolor"] = "#E5E5E5"
    # gg.rcParams["axes.edgecolor"] = "bcbcbc"
    # gg.rcParams["axes.linewidth"] = "1"
    # gg.rcParams["axes.grid"] = "True"
    # gg.rcParams["axes.titlesize"] = "x-large"
    # gg.rcParams["axes.labelsize"] = "large"
    # gg.rcParams["axes.labelcolor"] = "black"
    # gg.rcParams["axes.axisbelow"] = "True"
    gg.rcParams["axes.color_cycle"] = ["#333333", "348ABD", "7A68A6", "A60628",
            "467821", "CF4457", "188487", "E24A33"]
    # gg.rcParams["grid.color"] = "white"
    # gg.rcParams["grid.linewidth"] = "1.4"
    # gg.rcParams["grid.linestyle"] = "solid"
    # gg.rcParams["xtick.major.size"] = "0"
    # gg.rcParams["xtick.minor.size"] = "0"
    # gg.rcParams["xtick.major.pad"] = "6"
    # gg.rcParams["xtick.minor.pad"] = "6"
    # gg.rcParams["xtick.color"] = "#7F7F7F"
    # gg.rcParams["xtick.direction"] = "out"  # pointing out of axis
    # gg.rcParams["ytick.major.size"] = "0"
    # gg.rcParams["ytick.minor.size"] = "0"
    # gg.rcParams["ytick.major.pad"] = "6"
    # gg.rcParams["ytick.minor.pad"] = "6"
    # gg.rcParams["ytick.color"] = "#7F7F7F"
    # gg.rcParams["ytick.direction"] = "out"  # pointing out of axis
    gg.rcParams["legend.fancybox"] = "True"
    gg.rcParams["figure.figsize"] = "11, 8"
    gg.rcParams["figure.facecolor"] = "1.0"
    gg.rcParams["figure.edgecolor"] = "0.50"
    gg.rcParams["figure.subplot.hspace"] = "0.5"


class theme_seaborn(theme):
    """
    Theme for seaborn.

    Copied from mwaskom's seaborn:
        https://github.com/mwaskom/seaborn/blob/master/seaborn/rcmod.py

    Parameters
    ----------
    style : darkgrid | whitegrid | nogrid | ticks
        Style of axis background.
    context: notebook | talk | paper | poster
        Intended context for resulting figures.
    gridweight : extra heavy | heavy | medium | light
        Width of the grid lines. None
    """

    def __init__(self, style="darkgrid", gridweight=None, context="notebook"):
        self.style = style
        self.gridweight = gridweight
        self.context = context

    def __radd__(self, gg):
        gg = super(theme_seaborn, self).__radd__(gg)
        _set_default_theme_rcparams(gg, self.style, self.gridweight,
                self.context)
        gg.post_plot_callbacks.append(_theme_grey_post_plot_callback)
        return gg


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

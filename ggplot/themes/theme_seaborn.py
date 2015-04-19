import matplotlib as mpl
import matplotlib.pyplot as plt
from numpy import isreal

from .theme import theme


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

    def __init__(self, style="whitegrid",
                 gridweight=None, context="notebook"):
        super(theme_seaborn, self).__init__(complete=True)
        self.style = style
        self.gridweight = gridweight
        self.context = context
        self._set_theme_seaborn_rcparams(self._rcParams,
                                         self.style, self.gridweight,
                                         self.context)

    def _set_theme_seaborn_rcparams(self, rcParams, style,
                                    gridweight, context):
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

        rcParams.update(ax_params)

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

        rcParams.update(font_params)

        # Set other parameters
        rcParams.update({
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

        rcParams["timezone"] = "UTC"
        # rcParams["lines.linewidth"] = "1.0"
        # rcParams["lines.antialiased"] = "True"
        # rcParams["patch.linewidth"] = "0.5"
        # rcParams["patch.facecolor"] = "348ABD"
        # rcParams["patch.edgecolor"] = "#E5E5E5"
        rcParams["patch.antialiased"] = "True"
        rcParams["font.family"] = "sans-serif"
        rcParams["font.size"] = "12.0"
        rcParams["font.serif"] = ["Times", "Palatino",
                                  "New Century Schoolbook",
                                  "Bookman", "Computer Modern Roman",
                                  "Times New Roman"]
        rcParams["font.sans-serif"] = ["Helvetica", "Avant Garde",
                                       "Computer Modern Sans serif", "Arial"]
        # rcParams["axes.facecolor"] = "#E5E5E5"
        # rcParams["axes.edgecolor"] = "bcbcbc"
        # rcParams["axes.linewidth"] = "1"
        # rcParams["axes.grid"] = "True"
        # rcParams["axes.titlesize"] = "x-large"
        # rcParams["axes.labelsize"] = "large"
        # rcParams["axes.labelcolor"] = "black"
        # rcParams["axes.axisbelow"] = "True"
        rcParams["axes.color_cycle"] = ["#333333", "348ABD", "7A68A6",
                                        "A60628", "467821", "CF4457",
                                        "188487", "E24A33"]
        # rcParams["grid.color"] = "white"
        # rcParams["grid.linewidth"] = "1.4"
        # rcParams["grid.linestyle"] = "solid"
        # rcParams["xtick.major.size"] = "0"
        # rcParams["xtick.minor.size"] = "0"
        # rcParams["xtick.major.pad"] = "6"
        # rcParams["xtick.minor.pad"] = "6"
        # rcParams["xtick.color"] = "#7F7F7F"
        # rcParams["xtick.direction"] = "out"  # pointing out of axis
        # rcParams["ytick.major.size"] = "0"
        # rcParams["ytick.minor.size"] = "0"
        # rcParams["ytick.major.pad"] = "6"
        # rcParams["ytick.minor.pad"] = "6"
        # rcParams["ytick.color"] = "#7F7F7F"
        # rcParams["ytick.direction"] = "out"  # pointing out of axis
        rcParams["legend.fancybox"] = "True"
        rcParams["figure.figsize"] = "11, 8"
        rcParams["figure.facecolor"] = "1.0"
        rcParams["figure.edgecolor"] = "0.50"
        rcParams["figure.subplot.hspace"] = "0.5"

    def apply_theme(self, ax):
        """
        Styles x,y axes to appear like ggplot2
        Must be called after all plot and axis manipulation operations have
        been carried out (needs to know final tick spacing)

        From:
        https://github.com/wrobstory/climatic/blob/master/climatic/stylers.py
        """
        # TODO: Customize for the different seaborn styles
        # Remove axis border
        for child in ax.get_children():
            if isinstance(child, mpl.spines.Spine):
                child.set_alpha(0)

        # Restyle the tick lines
        for line in ax.get_xticklines() + ax.get_yticklines():
            line.set_markersize(5)
            line.set_markeredgewidth(mpl.rcParams['grid.linewidth'])

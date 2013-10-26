from .theme import theme

def _set_default_theme_rcparams(gg):
    """helper method to set the default rcParams"""
    gg.rcParams["timezone"] = "UTC"
    gg.rcParams["lines.linewidth"] = "1.0"
    gg.rcParams["lines.antialiased"] = "True"
    gg.rcParams["patch.linewidth"] = "0.5"
    gg.rcParams["patch.facecolor"] = "348ABD"
    gg.rcParams["patch.edgecolor"] = "#E5E5E5"
    gg.rcParams["patch.antialiased"] = "True"
    gg.rcParams["font.family"] = "sans-serif"
    gg.rcParams["font.size"] = "12.0"
    gg.rcParams["font.serif"] = ["Times", "Palatino", "New Century Schoolbook", "Bookman", "Computer Modern Roman", "Times New Roman"]
    gg.rcParams["font.sans-serif"] = ["Helvetica", "Avant Garde", "Computer Modern Sans serif", "Arial"]
    gg.rcParams["axes.facecolor"] = "eeeeee"
    gg.rcParams["axes.edgecolor"] = "bcbcbc"
    gg.rcParams["axes.linewidth"] = "1"
    gg.rcParams["axes.grid"] = "True"
    gg.rcParams["axes.titlesize"] = "x-large"
    gg.rcParams["axes.labelsize"] = "large"
    gg.rcParams["axes.labelcolor"] = "black"
    gg.rcParams["axes.axisbelow"] = "True"
    gg.rcParams["axes.color_cycle"] = [ "#333333", "348ABD", "7A68A6", "A60628", "467821", "CF4457", "188487", "E24A33" ]
    gg.rcParams["grid.color"] = "white"
    gg.rcParams["grid.linewidth"] = "1"
    gg.rcParams["grid.linestyle"] = "solid"
    gg.rcParams["xtick.major.size"] = "0"
    gg.rcParams["xtick.minor.size"] = "0"
    gg.rcParams["xtick.major.pad"] = "6"
    gg.rcParams["xtick.minor.pad"] = "6"
    gg.rcParams["xtick.color"] = "#7F7F7F"
    gg.rcParams["xtick.direction"] = "in"
    gg.rcParams["ytick.major.size"] = "0"
    gg.rcParams["ytick.minor.size"] = "0"
    gg.rcParams["ytick.major.pad"] = "6"
    gg.rcParams["ytick.minor.pad"] = "6"
    gg.rcParams["ytick.color"] = "#7F7F7F"
    gg.rcParams["ytick.direction"] = "in"
    gg.rcParams["legend.fancybox"] = "True"
    gg.rcParams["figure.figsize"] = "11, 8"
    gg.rcParams["figure.facecolor"] = "1.0"
    gg.rcParams["figure.edgecolor"] = "0.50"
    gg.rcParams["figure.subplot.hspace"] = "0.5"


class theme_gray(theme):
    """
    Standard theme for ggplot. Gray background w/ white gridlines.

    Copied from the the ggplot2 codebase:
        https://github.com/hadley/ggplot2/blob/master/R/theme-defaults.r
    """
    def __radd__(self, gg):
        gg = super(theme_gray, self).__radd__(gg)
        _set_default_theme_rcparams(gg)
        return gg

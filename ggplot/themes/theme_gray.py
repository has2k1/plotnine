import matplotlib as mpl


class theme_gray(object):
    """
    Standard theme for ggplot. Gray background w/ white gridlines.

    Copied from the the ggplot2 codebase:
        https://github.com/hadley/ggplot2/blob/master/R/theme-defaults.r
    """
    def __init__(self):

        mpl.rcParams["backend"] = "MacOSX"
        mpl.rcParams["interactive"] = "True"
        mpl.rcParams["toolbar"] = "toolbar2"
        mpl.rcParams["timezone"] = "UTC"
        mpl.rcParams["lines.linewidth"] = "1.0"
        mpl.rcParams["lines.antialiased"] = "True"
        mpl.rcParams["patch.linewidth"] = "0.5"
        mpl.rcParams["patch.facecolor"] = "348ABD"
        mpl.rcParams["patch.edgecolor"] = "#E5E5E5"
        mpl.rcParams["patch.antialiased"] = "True"
        mpl.rcParams["font.family"] = "serif"
        mpl.rcParams["font.size"] = "12.0"
        mpl.rcParams["font.serif"] = ["Times", "Palatino", "New Century Schoolbook", "Bookman", "Computer Modern Roman"]
        mpl.rcParams["font.sans-serif"] = ["Helvetica", "Avant Garde", "Computer Modern Sans serif"]
        mpl.rcParams["axes.facecolor"] = "eeeeee"
        mpl.rcParams["axes.edgecolor"] = "bcbcbc"
        mpl.rcParams["axes.linewidth"] = "1"
        mpl.rcParams["axes.grid"] = "True"
        mpl.rcParams["axes.titlesize"] = "x-large"
        mpl.rcParams["axes.labelsize"] = "large"
        mpl.rcParams["axes.labelcolor"] = "black"
        mpl.rcParams["axes.axisbelow"] = "True"
        mpl.rcParams["axes.color_cycle"] = [ "#333333", "348ABD", "7A68A6", "A60628", "467821", "CF4457", "188487", "E24A33" ]
        mpl.rcParams["grid.color"] = "white"
        mpl.rcParams["grid.linewidth"] = "1"
        mpl.rcParams["grid.linestyle"] = "solid"
        mpl.rcParams["xtick.major.size"] = "0"
        mpl.rcParams["xtick.minor.size"] = "0"
        mpl.rcParams["xtick.major.pad"] = "6"
        mpl.rcParams["xtick.minor.pad"] = "6"
        mpl.rcParams["xtick.color"] = "#7F7F7F"
        mpl.rcParams["xtick.direction"] = "in"
        mpl.rcParams["ytick.major.size"] = "0"
        mpl.rcParams["ytick.minor.size"] = "0"
        mpl.rcParams["ytick.major.pad"] = "6"
        mpl.rcParams["ytick.minor.pad"] = "6"
        mpl.rcParams["ytick.color"] = "#7F7F7F"
        mpl.rcParams["ytick.direction"] = "in"
        mpl.rcParams["legend.fancybox"] = "True"
        mpl.rcParams["figure.figsize"] = "11, 8"
        mpl.rcParams["figure.facecolor"] = "1.0"
        mpl.rcParams["figure.edgecolor"] = "0.50"
        mpl.rcParams["figure.subplot.hspace"] = "0.5"
        mpl.rcParams["keymap.fullscreen"] = "f"
        mpl.rcParams["keymap.home"] = [ "h", "r", "home" ]
        mpl.rcParams["keymap.back"] = [ "left", "c", "backspace" ]
        mpl.rcParams["keymap.forward"] = [ "right", "v" ]
        mpl.rcParams["keymap.pan"] = "p"
        mpl.rcParams["keymap.zoom"] = "o"
        mpl.rcParams["keymap.save"] = "s"
        mpl.rcParams["keymap.grid"] = "g"
        mpl.rcParams["keymap.yscale"] = "l"
        mpl.rcParams["keymap.xscale"] = [ "L", "k" ]
        mpl.rcParams["keymap.all_axes"] = "a"
    
    def __radd__(self, gg):
        return gg

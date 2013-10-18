import matplotlib as mpl


class theme_gray(object):
    """
    Standard theme for ggplot. Gray background w/ white gridlines.

    Copied from the the ggplot2 codebase:
        https://github.com/hadley/ggplot2/blob/master/R/theme-defaults.r
    """
    def __init__(self):
        mpl.rcParams['figure.facecolor'] = '1.0'
        mpl.rcParams['axes.facecolor'] = '#E5E5E5'
        mpl.rcParams['grid.color'] = 'white'
        mpl.rcParams['grid.linewidth'] = '1'
        mpl.rcParams['grid.linestyle'] = 'solid'

        mpl.rcParams['axes.labelcolor'] =  'black'
        mpl.rcParams['xtick.color'] = 'black'
        mpl.rcParams['ytick.color'] = 'black'
    
    def __radd__(self, gg):
        return gg

from .theme_gray import theme_gray


class theme_bw(theme_gray):
    """
    White background w/ black gridlines
    """

    def __init__(self):
        theme_gray.__init__(self)
        d = {
            'axes.facecolor': 'white',
            'grid.linewidth': '0.5',
            'grid.color': '#E5E5E5',
            'xtick.color': 'black',
            'ytick.color': 'black',
        }
        self._rcParams.update(d)

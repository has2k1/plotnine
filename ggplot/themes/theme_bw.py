from .theme_gray import theme_gray


class theme_bw(theme_gray):
    """
    White background w/ black gridlines
    """

    def __init__(self):
        super(theme_bw, self).__init__()
        self._rcParams['axes.facecolor'] = 'white'

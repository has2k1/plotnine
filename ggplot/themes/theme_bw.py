from .theme_gray import theme_gray


class theme_bw(theme_gray):
    """
    White background w/ black gridlines
    """

    def apply_rcparams(self, rcParams):
        super(theme_bw, self).apply_rcparams(rcParams)
        rcParams['axes.facecolor'] = 'white'

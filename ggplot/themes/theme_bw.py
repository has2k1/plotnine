from .theme_gray import theme_gray


class theme_bw(theme_gray):
    """
    White background w/ black gridlines
    """

    # @todo: change theme_gray to use self._rcParams and just update the
    # existing self._rcParams

    # def __radd__(self, gg):
    #     # no need to copy as super will do it...
    #     gg = super(theme_bw, self).__radd__(gg)
    #     gg.rcParams['axes.facecolor'] = 'white'
    #     return gg

    def apply_rcparams(self, rcParams):
        super(theme_bw, self).apply_rcparams(rcParams)
        rcParams['axes.facecolor'] = 'white'

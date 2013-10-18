import matplotlib as mpl
from .theme_gray import theme_gray

class theme_bw(theme_gray):
    def __init__(self):
        super(theme_gray, self).__init__()
        mpl.rcParams['axes.facecolor'] = 'white'

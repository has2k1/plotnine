from .theme_matplotlib import theme_matplotlib
import matplotlib.pyplot as plt
import matplotlib as mpl

class theme_xkcd(theme_matplotlib):
    """
    xkcd theme
    
    The theme internaly uses the settings from pyplot.xkcd().
    """
    def __init__(self, scale=1, length=100, randomness=2):
        self._rcParams={}
        with plt.xkcd(scale=scale, length=length, randomness=randomness):
            _xkcd = mpl.rcParams.copy()
        self._rcParams.update(_xkcd)

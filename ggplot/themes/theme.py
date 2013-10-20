import matplotlib as mpl
from theme_gray import theme_gray

class theme(theme_gray):
    def __init__(self, params):
        # Load the default gray theme then customize on top of it
        super(theme_gray, self).__init__()
        for param, value in params.items():
            mpl.rcParams[param] = str(value)

    def __radd__(self, gg):
        return gg

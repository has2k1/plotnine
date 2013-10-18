import matplotlib as mpl


class theme_gray(object):
    def __radd__(self, gg):
        mpl.rcParams['figure.facecolor'] = '1.0'
        mpl.rcParams['axes.facecolor'] = '#E5E5E5'
        mpl.rcParams['grid.color'] = 'white'
        mpl.rcParams['grid.linewidth'] = '1'
        mpl.rcParams['grid.linestyle'] = 'solid'

        mpl.rcParams['axes.labelcolor'] =  'black'
        mpl.rcParams['xtick.color'] = 'black'
        mpl.rcParams['ytick.color'] = 'black'

        return gg

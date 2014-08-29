from .theme import theme
import matplotlib as mpl


class theme_matplotlib(theme):
    """
    The default matplotlib look and feel.

    The theme can be used (and has the same parameter to customize) like a
    matplotlib rc_context() manager.

    Parameters
    -----------
    rc :  dict of rcParams
        rcParams which should be aplied on top of mathplotlib default
    fname :  Filename (str)
        a filename to a matplotlibrc file
    matplotlib_defaults : bool
        if True (the default) resets the plot setting to the (current)
        matplotlib.rcParams values
    """

    def __init__(self, rc=None, fname=None, matplotlib_defaults=True):
        super(theme_matplotlib, self).__init__(complete=True)

        self._rcParams = {}
        if matplotlib_defaults:
            _copy = mpl.rcParams.copy()
            # no need to a get a deprecate warning just because
            # they are still included in rcParams...
            for key in mpl._deprecated_map:
                if key in _copy:
                    del _copy[key]
            if 'tk.pythoninspect' in _copy:
                del _copy['tk.pythoninspect']
            self._rcParams.update(_copy)
        if fname:
            self._rcParams.update(mpl.rc_params_from_file(fname))
        if rc:
            self._rcParams.update(rc)

    def apply_theme(self, ax, params):
        """
        Styles x,y axes to appear like ggplot2
        Must be called after all plot and axis manipulation operations have
        been carried out (needs to know final tick spacing)

        From:
        https://github.com/wrobstory/climatic/blob/master/climatic/stylers.py
        """
        # set parameters
        for att, val in params['xaxis']:
            getattr(ax.xaxis, att)(val)

        for att, val in params['yaxis']:
            getattr(ax.yaxis, att)(val)

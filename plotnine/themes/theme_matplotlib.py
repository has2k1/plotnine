import matplotlib as mpl

from ..options import get_option
from .theme import theme
from .elements import element_rect


class theme_matplotlib(theme):
    """
    The default matplotlib look and feel.

    The theme can be used (and has the same parameter
    to customize) like a :class:`matplotlib.rc_context` manager.

    Parameters
    -----------
    rc :  dict, optional
        rcParams which should be applied on top of
        mathplotlib default.
    fname : str, optional
        Filename to a matplotlibrc file
    use_defaults : bool
        If `True` (the default) resets the plot setting
        to the (current) `matplotlib.rcParams` values
    """

    def __init__(self, rc=None, fname=None, use_defaults=True):
        theme.__init__(
            self,
            aspect_ratio=get_option('aspect_ratio'),
            dpi=get_option('dpi'),
            figure_size=get_option('figure_size'),
            legend_key=element_rect(fill='None', colour='None'),
            legend_key_size=16,
            panel_spacing=0.1,
            strip_background=element_rect(
                fill='#D9D9D9', color='#D9D9D9', size=1),
            complete=True)

        if use_defaults:
            _copy = mpl.rcParams.copy()
            deprecated_rcparams = (
                set(mpl._deprecated_remain_as_none)
                | set(mpl._all_deprecated)
            )
            # no need to a get a deprecate warning just because
            # they are still included in rcParams...
            for key in deprecated_rcparams:
                if key in _copy:
                    del _copy[key]
            if 'tk.pythoninspect' in _copy:
                del _copy['tk.pythoninspect']
            self._rcParams.update(_copy)

        if fname:
            self._rcParams.update(mpl.rc_params_from_file(fname))
        if rc:
            self._rcParams.update(rc)

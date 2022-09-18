import matplotlib as mpl

from ..options import get_option
from .theme import theme
from .elements import element_rect, element_text


class theme_matplotlib(theme):
    """
    The default matplotlib look and feel.

    The theme can be used (and has the same parameter
    to customize) like a :class:`matplotlib.rc_context` manager.

    Parameters
    ----------
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
            text=element_text(
                size=mpl.rcParams['font.size'],
                linespacing=1,
            ),

            aspect_ratio=get_option('aspect_ratio'),
            dpi=get_option('dpi'),
            figure_size=get_option('figure_size'),

            axis_text=element_text(
                margin={'t': 2.4, 'r': 2.4, 'units': 'pt'}
            ),
            axis_title=element_text(
                margin={'t': 5, 'r': 5, 'units': 'pt'}
            ),

            legend_box='auto',
            legend_box_just='auto',
            legend_box_margin=10,
            legend_box_spacing=0.1,
            legend_direction='auto',
            legend_entry_spacing_x=5,
            legend_entry_spacing_y=2,
            legend_key=element_rect(fill='None', colour='None'),
            legend_key_size=16,
            legend_margin=10,
            legend_position='right',
            legend_spacing=10,
            legend_text=element_text(
                margin={'t': 3, 'b': 3, 'l': 3, 'r': 3, 'units': 'pt'}
            ),
            legend_title=element_text(ha='left', margin={'b': 8}),
            legend_title_align='auto',
            panel_spacing=0.1,
            plot_caption=element_text(
                margin={'t': 7.2, 'r': 0, 'units': 'pt'}
            ),
            plot_title=element_text(
                ha='center',
                linespacing=1.2,
                margin={'b': 6.6, 'units': 'pt'}
            ),
            strip_background=element_rect(
                fill='#D9D9D9',
                color='#D9D9D9',
                size=1
            ),
            strip_margin=0,
            strip_text=element_text(
                margin={'t': 3, 'b': 3, 'l': 3, 'r': 3, 'units': 'pt'}
            ),
            complete=True
        )

        if use_defaults:
            _copy = mpl.rcParams.copy()

            deprecated_rcparams = (
                # TODO: remove _all_deprecated < MPL 3.6.0
                set(getattr(mpl, '_deprecated_remain_as_none', {}))
                | set(getattr(mpl, '_all_deprecated', {}))
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

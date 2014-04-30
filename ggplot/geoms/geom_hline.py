from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from .geom import geom


class geom_hline(geom):
    DEFAULT_AES = {'color': 'black', 'linetype': 'solid',
                   'size': 1.0, 'alpha': None, 'y': None,
                   'xmin': None, 'xmax': None}
    REQUIRED_AES = {'yintercept'}
    DEFAULT_PARAMS = {'stat': 'hline', 'position': 'identity',
                      'show_guide': False}

    _aes_renames = {'size': 'linewidth', 'linetype': 'linestyle'}
    _units = {'alpha'}

    def _plot_unit(self, pinfo, ax):
        del pinfo['y']
        xmin = pinfo.pop('xmin')
        if xmin is None:
            xmin, _ = ax.get_xlim()

        xmax = pinfo.pop('xmax')
        if xmax is None:
            _, xmax = ax.get_xlim()

        y = pinfo.pop('yintercept')
        # TODO: if y is not the same length as
        # the other aesthetics, default aesthetics should
        # should be for the array-like aesthetics
        ax.hlines(y, xmin, xmax, **pinfo)

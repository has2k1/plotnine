from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from .geom import geom


class geom_hline(geom):
    DEFAULT_AES = {'color': 'black', 'linetype': 'solid',
                   'size': 1.0, 'alpha': None}
    DEFAULT_PARAMS = {'stat': 'hline', 'position': 'identity',
                      'show_guide': False, 'label': ''}

    _aes_renames = {'size': 'linewidth', 'linetype': 'linestyle'}
    _groups = {'alpha'}

    def _plot_unit(self, pinfo, ax):
        pinfo['label'] = self.params['label']
        try:
            xmin = pinfo.pop('xmin')
        except KeyError:
            xmin, _ = ax.get_xlim()
        try:
            xmax = pinfo.pop('xmax')
        except KeyError:
            _, xmax = ax.get_xlim()

        y = pinfo.pop('yintercept')
        # TODO: if y is not the same length as
        # the other aesthetics, default aesthetics should
        # should be for the array-like aesthetics
        ax.hlines(y, xmin, xmax, **pinfo)

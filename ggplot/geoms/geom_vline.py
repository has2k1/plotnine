from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from .geom import geom


class geom_vline(geom):
    DEFAULT_AES = {'color': 'black', 'linetype': 'solid',
                   'size': 1.0, 'alpha': None}
    DEFAULT_PARAMS = {'stat': 'vline', 'position': 'identity',
                      'show_guide': False, 'label': ''}

    _aes_renames = {'size': 'linewidth', 'linetype': 'linestyle'}
    _groups = {'alpha'}

    def _plot_unit(self, pinfo, ax):
        pinfo['label'] = self.params['label']
        try:
            ymin = pinfo.pop('ymin')
        except KeyError:
            ymin, _ = ax.get_ylim()
        try:
            ymax = pinfo.pop('ymax')
        except KeyError:
            _, ymax = ax.get_ylim()

        x = pinfo.pop('xintercept')
        # TODO: if x is not the same length as
        # the other aesthetics, default aesthetics should
        # should be for the array-like aesthetics
        # problem illustrated by:
        # gg = ggplot(aes(x="x", y="y", shape="cat2",
        #             color="cat"), data=df)
        # gg + geom_point() + geom_vline(xintercept=40)
        ax.vlines(x, ymin, ymax, **pinfo)

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from .geom import geom


class geom_vline(geom):
    DEFAULT_AES = {'color': 'black', 'linetype': 'solid',
                   'size': 1.0, 'alpha': None, 'ymin': None,
                   'ymax': None}
    REQUIRED_AES = {'xintercept'}
    DEFAULT_PARAMS = {'stat': 'vline', 'position': 'identity',
                      'show_guide': False}

    _aes_renames = {'size': 'linewidth', 'linetype': 'linestyle'}
    _units = {'alpha'}

    def _plot_unit(self, pinfo, ax):
        ymin = pinfo.pop('ymin')
        if ymin is None:
            ymin, _ = ax.get_ylim()

        ymax = pinfo.pop('ymax')
        if ymax is None:
            _, ymax = ax.get_ylim()

        x = pinfo.pop('xintercept')
        # TODO: if x is not the same length as
        # the other aesthetics, default aesthetics
        # should be for the array-like aesthetics
        # problem illustrated by:
        # gg = ggplot(aes(x="x", y="y", shape="cat2",
        #             color="cat"), data=df)
        # gg + geom_point() + geom_vline(xintercept=40)
        # vertical line should be black
        #
        # This is probably a good test for handling
        # aesthetics properly along the whole pipeline.
        # The problem should clear up when that is the case,
        # and the above code should be added as a test case
        ax.vlines(x, ymin, ymax, **pinfo)

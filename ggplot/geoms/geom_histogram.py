from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import sys
from .geom import geom


# TODO: Why the difference between geom_bar and geom_histogram?
class geom_histogram(geom):
    DEFAULT_AES = {'alpha': None, 'color': None, 'fill': '#333333',
                   'linetype': 'solid', 'size': 1.0, 'weight': None}
    REQUIRED_AES = {'x'}
    DEFAULT_PARAMS = {'stat': 'bin', 'position': 'stack', 'label': ''}

    _aes_renames = {'linetype': 'linestyle', 'size': 'linewidth',
                    'fill': 'facecolor', 'color': 'edgecolor'}
    _groups = {'alpha', 'edgecolor', 'facecolor', 'linestyle', 'linewidth'}

    def __init__(self, *args, **kwargs):
        super(geom_histogram, self).__init__(*args, **kwargs)
        self._warning_printed = False

    def _plot_unit(self, pinfo, ax):
        pinfo['label'] = self.params['label']
        weight = pinfo.pop('weight')

        if 'binwidth' in pinfo:
            binwidth = pinfo.pop('binwidth')
            try:
                binwidth = float(binwidth)
                bottom = np.nanmin(pinfo['x'])
                top = np.nanmax(pinfo['x'])
                pinfo['bins'] = np.arange(bottom, top + binwidth, binwidth)
            except:
                pass
        if 'bins' not in pinfo:
            pinfo['bins'] = 30
            if not self._warning_printed:
                sys.stderr.write("binwidth defaulted to range/30. " +
                             "Use 'binwidth = x' to adjust this.\n")
                self._warning_printed = True

        ax.hist(**pinfo)

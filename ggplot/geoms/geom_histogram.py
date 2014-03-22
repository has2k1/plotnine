from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import sys
from .geom import geom


class geom_histogram(geom):
    VALID_AES = {'x', 'alpha', 'color', 'fill', 'linetype',
                 'size', 'weight'}
    REQUIRED_AES = {'x'}
    DEFAULT_PARAMS = {'stat': 'bin', 'position': 'stack', 'label': ''}
    
    _groups = {'color', 'alpha', 'shape'}
    _aes_renames = {'linetype': 'linestyle'}

    def __init__(self, *args, **kwargs):
        super(geom_histogram, self).__init__(*args, **kwargs)
        self._warning_printed = False

    def _plot_unit(self, pinfo, ax):
        pinfo['label'] = self.params['label']

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

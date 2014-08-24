from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np

from ..utils.exceptions import gg_warning
from .geom import geom


class geom_line(geom):
    DEFAULT_AES = {'color': 'black', 'alpha': None, 'linetype': 'solid',
                   'size': 1.0}
    REQUIRED_AES = {'x', 'y'}
    DEFAULT_PARAMS = {'stat': 'identity', 'position': 'identity'}

    _aes_renames = {'size': 'linewidth', 'linetype': 'linestyle'}
    _units = {'alpha', 'color', 'linestyle'}

    def draw(self, pinfo, scales, ax, **kwargs):
        if 'linewidth' in pinfo and isinstance(pinfo['linewidth'], list):
            # ggplot also supports aes(size=...) but the current mathplotlib
            # is not. See https://github.com/matplotlib/matplotlib/issues/2658
            pinfo['linewidth'] = 4
            msg = """\
            'geom_line()' currenty does not support the mapping of \
            size ('aes(size=<var>'), using size=4 as a replacement.
            Use 'geom_line(size=x)' to set the size for the whole line.
            """
            gg_warning(msg)

        pinfo = self.sort_by_x(pinfo)
        x = pinfo.pop('x')
        y = pinfo.pop('y')

        idx = np.argsort(x)
        x = [x[i] for i in idx]
        y = [y[i] for i in idx]

        ax.plot(x, y, **pinfo)

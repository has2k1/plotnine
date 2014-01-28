from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from .theme_gray import theme_gray

class theme_bw(theme_gray):
    """
    White background w/ black gridlines
    """
   
    def __radd__(self, gg):
        # no need to copy as super will do it...
        gg = super(theme_bw, self).__radd__(gg)
        gg.rcParams['axes.facecolor'] = 'white'
        return gg
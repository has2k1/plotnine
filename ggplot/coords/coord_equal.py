from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from copy import deepcopy


class coord_equal(object):

    def __radd__(self, gg):
        gg = deepcopy(gg)
        gg.coord_equal = True
        return gg



from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from copy import deepcopy
import math
from ..utils.utils import add_ggplotrc_params


class facet_grid(object):
    def __init__(self, x=None, y=None, nrow=None, ncol=None, scales=None):
        add_ggplotrc_params(self)
        self.x = x
        self.y = y
        self.ncol = nrow
        self.nrow = ncol
        self.scales = scales

    def __radd__(self, gg):
        x = gg.data.get(self.x)
        y = gg.data.get(self.y)

        if x is None and y is None:
            raise Exception("No facets provided!")
        
        # only do the deepcopy after the check
        gg = deepcopy(gg)

        if x is None:
            n_dim_x = 1
        else:
            n_dim_x = x.nunique()
        if y is None:
            n_dim_y = 1
        else:
            n_dim_y = y.nunique()
        
        n_dim = n_dim_x * n_dim_y
        if self.ncol is None and self.nrow is None:
            n_rows = n_dim_x
            n_cols = n_dim_y
        elif self.nrow is None:
            n_rows = self.ncol
            n_cols = math.ceil(float(n_dim) / n_rows)
        elif self.ncol is None:
            n_cols = self.nrow
            n_rows = math.ceil(float(n_dim) / n_cols)
        else:
            n_rows = self.ncol
            n_cols = self.nrow

        gg.n_rows, gg.n_columns = int(n_rows), int(n_cols)

        facets = []
        if self.x:
            facets.append(self.x)
        if self.y:
            facets.append(self.y)
        gg.facets = facets
        gg.facet_type = "grid"
        gg.facet_scales = self.scales

        return gg

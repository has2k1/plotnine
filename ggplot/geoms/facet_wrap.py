from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from copy import deepcopy
import math
from ..utils.utils import add_ggplotrc_params

class facet_wrap(object):
    def __init__(self, x=None, y=None, ncol=None, nrow=None, scales="free"):
        if x is None and y is None:
            raise Exception("You need to specify a variable name: facet_wrap('var')")
        add_ggplotrc_params(self)
        self.x = x
        self.y = y
        self.ncol = ncol
        self.nrow = nrow
        self.scales = scales

    def __radd__(self, gg):
        # deepcopy must be the first thing to not change the original object
        gg = deepcopy(gg)
        
        x, y = None, None
        gg.n_dim_x = 1
        facets = []
        if self.x:
            x = gg.data.get(self.x)
            gg.n_dim_x = x.nunique()
            facets.append(self.x)
        if self.y:
            y = gg.data.get(self.y)
            gg.n_dim_x *= y.nunique()
            facets.append(self.y)

        n_rows = self.nrow
        n_cols = self.ncol

        if n_rows is None and n_cols is None:
            # calculate both on the fly
            n_rows = math.ceil(math.sqrt(gg.n_dim_x))
            n_cols = math.ceil(gg.n_dim_x / math.ceil(math.sqrt(gg.n_dim_x)))
        elif n_rows is None:
            # calculate n_rows on the fly
            n_rows = math.ceil(float(gg.n_dim_x) / n_cols)
        elif n_cols is None:
            # calculate n_columns on the fly
            n_cols = math.ceil(float(gg.n_dim_x) / n_rows)

        gg.n_rows, gg.n_columns = int(n_rows), int(n_cols)

        gg.facets = facets
        gg.facet_type = "wrap"
        gg.facet_scales = self.scales
        
        return gg

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
        
        x,y = None, None
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

        n_wide = self.ncol
        n_high = self.nrow

        if n_wide is None and n_high is None:
            # calculate both on the fly
            n_wide = math.ceil(math.sqrt(gg.n_dim_x))
            n_high = math.ceil(gg.n_dim_x / math.ceil(math.sqrt(gg.n_dim_x)))
        elif n_wide is None:
            # calculate n_wide on the fly
            n_wide = math.ceil(float(gg.n_dim_x) / n_high)
        elif n_high is None:
            # calculate n_high on the fly
            n_high = math.ceil(float(gg.n_dim_x) / n_wide)

        gg.n_wide, gg.n_high = int(n_wide), int(n_high)

        gg.facets = facets
        gg.facet_type = "wrap"
        gg.facet_scales = self.scales
        
        return gg

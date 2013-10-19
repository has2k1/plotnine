from copy import deepcopy
import math

class facet_wrap(object):
    def __init__(self, x=None, ncol=None, nrow=None, scales="free"):
        self.x = x
        self.ncol = ncol
        self.nrow = nrow
        self.scales = scales

    def __radd__(self, gg):

        x = gg.data.get(self.x)
        if x is None:
            n_wide = 1
        else:
            n_wide = x.nunique()
            gg.n_dim_x = x.nunique()

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
        facets = []
        facets.append(self.x)
        gg.facets = facets
        gg.facet_type = "wrap"
        gg.facet_scales = self.scales

        return deepcopy(gg)

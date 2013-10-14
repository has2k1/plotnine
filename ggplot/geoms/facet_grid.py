from copy import deepcopy


class facet_grid(object):
    def __init__(self, x=None, y=None, scales="free"):
        self.x = x
        self.y = y
        self.scales = scales

    def __radd__(self, gg):

        x = gg.data.get(self.x)
        y = gg.data.get(self.y)
        if x is None:
            n_wide = 1
        else:
            n_wide = x.nunique()
        if y is None:
            n_high = 1
        else:
            n_high = y.nunique()
        
        gg.n_wide, gg.n_high = n_wide, n_high
        facets = []
        if self.x:
            facets.append(self.x)
        if self.y:
            facets.append(self.y)
        gg.facets = facets
        gg.facet_type = "grid"
        gg.facet_scales = self.scales

        combos = []
        for x_i in sorted(x.unique()):
            for y_i in sorted(y.unique()):
                combos.append((x_i, y_i))
        gg.facet_pairs = combos

        return deepcopy(gg)

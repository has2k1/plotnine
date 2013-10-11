from copy import deepcopy


class facet_grid(object):
    def __init__(self, x=None, y=None):
        self.x = x
        self.y = y

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

        return deepcopy(gg)

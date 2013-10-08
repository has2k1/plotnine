from copy import deepcopy


class facet_grid(object):
    def __init__(self, x=None, y=None):
        self.x = x
        self.y = y

    def __radd__(self, gg):

        x = gg.data.get(self.x)
        y = gg.data.get(self.y)
        if x is None:
            n_dim_x = 1
        else:
            n_dim_x = x.nunique()
        if y is None:
            n_dim_y = 1
        else:
            n_dim_y = y.nunique()
        
        gg.n_dim_x, gg.n_dim_y = n_dim_x, n_dim_y
        facets = []
        if self.x:
            facets.append(self.x)
        if self.y:
            facets.append(self.y)
        gg.facets = facets

        return deepcopy(gg)

from __future__ import absolute_import, division, print_function


class facet(object):
    ncol = None
    nrow = None
    as_table = True
    drop = True
    shrink = True
    free = {'x': True, 'y': True}

    def __init__(self, scales='fixed', shrink=True,
                 labeller='label_value', as_table=True,
                 drop=True):
        from .labelling import as_labeller
        self.shrink = shrink
        self.labeller = as_labeller(labeller)
        self.as_table = as_table
        self.drop = drop
        self.free = {'x': scales in ('free_x', 'free'),
                     'y': scales in ('free_y', 'free')}

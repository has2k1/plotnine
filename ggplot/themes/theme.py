from copy import deepcopy

class theme(object):
    def __radd__(self, gg):
        gg = deepcopy(gg)
        return gg
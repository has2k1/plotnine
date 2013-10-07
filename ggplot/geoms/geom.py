from copy import deepcopy

class geom(object):
    def __init__(self, **kwargs):
        self.manual_aes = {k: v for k, v in kwargs.iteritems() if k in self.VALID_AES}

    def __radd__(self, gg):
        gg = deepcopy(gg)
        gg.geoms.append(self)
        return gg
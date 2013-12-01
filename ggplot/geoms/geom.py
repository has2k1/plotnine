from copy import deepcopy
from ggplot.components import aes

__ALL__ = ["geom"]

class geom(object):
    def __init__(self, *args, **kwargs):
        if "colour" in kwargs:
            kwargs["color"] = kwargs["colour"]
            del kwargs["colour"]
        if len(args)==1:
            if isinstance(args[0], aes):
                self.manual_aes = {k: v for k, v in kwargs.items() if k in self.VALID_AES}
                return
        self.manual_aes = {k: v for k, v in kwargs.items() if k in self.VALID_AES}

    def __radd__(self, gg):
        gg = deepcopy(gg)
        gg.geoms.append(self)
        return gg

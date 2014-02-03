from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from copy import deepcopy
from ggplot.components import aes
from pandas import DataFrame

__ALL__ = ["geom"]

class geom(object):
    """Base class of all Geoms"""
    VALID_AES = []
    data = None
    aes = None
    def __init__(self, *args, **kwargs):
        # new dict for each geom
        self.aes = {}
        for arg in args:
            if isinstance(arg, aes):
                for k, v in arg.items():
                    if k in self.VALID_AES:
                        self.aes[k] = v
            elif isinstance(arg, DataFrame):
                self.data = arg
            else:
                raise Exception('Unknown argument of type "{0}".'.format(type(arg)))
        if "data" in kwargs:
            self.data = kwargs.pop("data")
        if "mapping" in kwargs:
            for k, v in kwargs.pop("mapping").items():
                if k in self.VALID_AES:
                    self.aes[k] = v
        if "colour" in kwargs:
            kwargs["color"] = kwargs["colour"]
            del kwargs["colour"]

        self.manual_aes = {}
        for k, v in kwargs.items():
            if k in self.VALID_AES:
                self.manual_aes[k] = v

    def __radd__(self, gg):
        gg = deepcopy(gg)
        gg.geoms.append(self)
        return gg


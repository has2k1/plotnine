from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import matplotlib.pyplot as plt
from copy import deepcopy

class theme(object):
    def __init__(self, *args, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __radd__(self, gg):
        gg = deepcopy(gg)
        gg.theme_applied = True
        return gg

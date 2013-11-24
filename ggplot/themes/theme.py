import matplotlib.pyplot as plt
from copy import deepcopy

class theme(object):
    def __radd__(self, gg):
        gg = deepcopy(gg)
        gg.rcParams['interactive'] = 'True'
        gg.theme_applied = True
        return gg
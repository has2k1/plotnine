from scale import scale
from copy import deepcopy

class scale_y_continuous(scale):
    def __radd__(self, gg):
        gg = deepcopy(gg)
        if self.label:
            gg.ylab = self.label
        if self.limits:
            gg.ylimits = self.limits
        if self.breaks:
            gg.ybreaks = self.breaks
        return gg


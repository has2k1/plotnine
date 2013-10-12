from scale import scale
from copy import deepcopy

class scale_x_continuous(scale):
    VALID_SCALES = ['name', 'limits', 'breaks', 'trans']
    def __radd__(self, gg):
        gg = deepcopy(gg)
        if self.name:
            gg.xlab = self.name
        if self.limits:
            gg.xlimits = self.limits
        if self.breaks:
            gg.xbreaks = self.breaks
        return gg

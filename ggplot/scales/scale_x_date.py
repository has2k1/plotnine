from scale import scale
from copy import deepcopy

class scale_x_date(scale):
    # include all valid scale_x_continuous scales
    VALID_SCALES = ['label', 'limits', 'breaks', 'trans']
    VALID_SCALES += ['breaks', 'minor_breaks']
    def __radd__(self, gg):
        gg = deepcopy(gg)
        if self.label:
            gg.xlab = self.label
        if self.limits:
            gg.xlimits = self.limits
        if self.breaks:
            gg.xbreaks = self.breaks
        return gg

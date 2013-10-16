from .scale import scale
from copy import deepcopy
from matplotlib.pyplot import FuncFormatter

dollar   = lambda x,pos: '$%1.2f' % x
currency = dollar
comma    = lambda x,pos: '{:0,d}'.format(int(x))
millions = lambda x, pos: '$%1.1fM' % (x*1e-6)

LABEL_FORMATS = {
    'comma': comma,
    'dollar': dollar,
    'currency': currency,
    'millions': millions
}

class scale_y_continuous(scale):
    VALID_SCALES = ['name', 'labels', 'limits', 'breaks', 'trans']
    def __radd__(self, gg):
        gg = deepcopy(gg)
        if self.name:
            gg.ylab = self.name.title()
        if self.labels and self.labels in LABEL_FORMATS:
            format_func = LABEL_FORMATS[self.labels]
            gg.ytick_formatter = FuncFormatter(format_func)
        if self.limits:
            gg.ylimits = self.limits
        if self.breaks:
            gg.ybreaks = self.breaks
        return gg


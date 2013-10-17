#!/usr/bin/env python
from ..utils import date_breaks, date_format
from .scale import scale
from copy import deepcopy


class scale_x_date(scale):
    """
    args:
        breaks => One of:
            1) a string specifying the width between breaks.
            2) the result of a valid call to `date_breaks`
            # TODO: third option not implemented yet
            3) a vector of breaks

    example:
        # 1) manually pass in breaks=date_breaks()

        print ggplot(meat, aes('date','beef')) + \
            geom_line() + \
            scale_x_date(breaks=date_breaks('10 years'),
                labels=date_format('%B %-d, %Y'))

        # 2) or breaks as just a string

        print ggplot(meat, aes('date','beef')) + \
            geom_line() + \
            scale_x_date(breaks='10 years',
                labels=date_format('%B %-d, %Y'))
    """
    VALID_SCALES = ['name', 'labels', 'limits', 'breaks', 'trans']
    def __radd__(self, gg):
        gg = deepcopy(gg)
        if self.name:
            gg.xlab = self.name.title()
        if self.labels:
            if isinstance(self.labels, basestring):
                self.labels = date_format(self.labels)
            gg.xtick_formatter = self.labels
        if self.limits:
            gg.xlimits = self.limits
        if self.breaks:
            if isinstance(self.breaks, basestring):
                self.breaks = date_breaks(self.breaks)
            gg.xmajor_locator = self.breaks
        return gg

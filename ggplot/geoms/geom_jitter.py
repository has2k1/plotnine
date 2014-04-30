from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from .geom_point import geom_point

class geom_jitter(geom_point):
    def __init__(self, *args, **kwargs):
        # jitter is just a special case of geom_point, so we'll just use
        # geom_point and then enforce jitter
        super(geom_point, self).__init__(*args, **kwargs)
        self.manual_aes['position'] = "jitter"

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
# default 1st argument is the name
class scale(object):
    VALID_SCALES = ['name', 'limits', 'breaks', 'trans']
    def __init__(self, *args, **kwargs):
        for s in self.VALID_SCALES:
            setattr(self, s, None)

        if args:
            self.name = args[0]

        for k, v in kwargs.items():
            if k in self.VALID_SCALES:
                setattr(self, k, v)


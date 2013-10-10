
# default 1st argument is the label
class scale(object):
    VALID_SCALES = ['label', 'limits', 'breaks', 'trans']
    def __init__(self, *args, **kwargs):
        for s in self.VALID_SCALES:
            setattr(self, s, None)

        if args:
            self.label = args[0]

        for k, v in kwargs.iteritems():
            if k in self.VALID_SCALES:
                setattr(self, k, v)


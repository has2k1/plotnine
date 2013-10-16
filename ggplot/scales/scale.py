

class scale(object):
    VALID_SCALES = []
    def __init__(self, *args, **kwargs):
        for s in self.VALID_SCALES:
            setattr(self, s, None)

        if args:
            self.name = args[0]

        for k, v in kwargs.items():
            if k in self.VALID_SCALES:
                setattr(self, k, v)


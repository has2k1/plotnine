from UserDict import UserDict

class aes(UserDict):
    DEFAULT_ARGS = ['x', 'y', 'color']
    def __init__(self, *args, **kwargs):
        if args:
            self.data = dict(zip(self.DEFAULT_ARGS, args))
        else:
            self.data = kwargs


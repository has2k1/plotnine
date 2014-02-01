from .utils import ggsave
from .date_breaks import date_breaks
from .date_format import date_format

__ALL__ = ["ggsave", "date_breaks", "date_format", "add_ggplotrc_params"]

class _rc_context(object):
    def __init__(self, fname=None):
        self.fname = fname
    def __enter__(self):
        import matplotlib as mpl
        self._rcparams = mpl.rcParams.copy()
        if self.fname:
            mpl.rcfile(self.fname)
    def __exit__(self, type, value, tb):
        import matplotlib as mpl
        mpl.rcParams.update(self._rcparams)

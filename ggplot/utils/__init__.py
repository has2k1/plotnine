from .utils import ggsave, add_ggplotrc_params
from .date_breaks import date_breaks
from .date_format import date_format

__all__ = ["ggsave", "date_breaks", "date_format", "add_ggplotrc_params"]
__all__ = [str(u) for u in __all__]

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

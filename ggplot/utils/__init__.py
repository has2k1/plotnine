from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from .ggutils import ggsave, add_ggplotrc_params
from .date_breaks import date_breaks
from .date_format import date_format
from .utils import (pop, is_categorical, is_string, is_scalar_or_string,
                    is_sequence_of_booleans, is_sequence_of_strings,
                    make_iterable, make_iterable_ntimes, waiver,
                    identity, discrete_dtypes, continuous_dtypes,
                    dataframe_id)

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

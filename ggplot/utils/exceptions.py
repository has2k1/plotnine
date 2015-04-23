from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from textwrap import dedent
import warnings


class GgplotError(Exception):
    """
    Exception for ggplot errors
    """
    def __init__(self, *args):
        args = [dedent(arg) for arg in args]
        self.message = " ".join(args)

    def __str__(self):
        return repr(self.message)


def gg_warning(message, category=UserWarning, stacklevel=2):
    """
    Show warning message

    Users of this function can use triple quoted strings or
    lists/tuples with worry less about indentation and the
    79 character limit.
    """
    if isinstance(message, (list, tuple)):
        message = ' '.join([dedent(s) for s in message])
    else:
        message = dedent(message)

    warnings.warn(message, category=category, stacklevel=stacklevel)

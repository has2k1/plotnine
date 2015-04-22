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


def gg_warning(text):
    warnings.warn(dedent(text))

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import textwrap
import warnings


class GgplotError(Exception):
    """
    Exception for ggplot errors
    """
    def __init__(self, *args):
        self.message = " ".join(args)

    def __str__(self):
        return repr(self.message)


def gg_warning(text):
    warnings.warn(textwrap.dedent(text))

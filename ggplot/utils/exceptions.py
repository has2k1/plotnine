from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import sys
import textwrap


class GgplotError(Exception):
    """
    Exception for ggplot errors
    """
    def __init__(self, *args):
        self.message = " ".join(args)

    def __str__(self):
        return repr(self.message)


def gg_warning(text):
    sys.stderr.write(
        textwrap.dedent(text))

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


_printed_warnings = set()


# TODO: use the warn package
def gg_warning(text):
    if not (text in _printed_warnings):
        _printed_warnings.add(text)
        sys.stderr.write(
            textwrap.dedent(text))


def gg_reset():
    """
    Cleanup after creating a plot
    """
    global _printed_warnings
    _printed_warnings = set()

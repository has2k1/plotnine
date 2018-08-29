from textwrap import dedent
import warnings

# Statsmodels is slow to fix upstream future warnings
# This module is imported before the stats module so
# so any FutureWarnings with the imports are suppressed
warnings.filterwarnings(
    'ignore',
    category=FutureWarning,
    module='statsmodels')

warnings.filterwarnings(
    'ignore',
    category=FutureWarning,
    module='pandas')

# These are rare
warnings.filterwarnings(
    'ignore',
    category=FutureWarning,
    module='scipy')


class PlotnineError(Exception):
    """
    Exception for ggplot errors
    """
    def __init__(self, *args):
        args = [dedent(arg) for arg in args]
        self.message = " ".join(args)

    def __str__(self):
        return repr(self.message)

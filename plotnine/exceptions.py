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


# Show the warnings on one line, leaving out any code makes the
# message clear
def warning_format(message, category, filename, lineno, file=None, line=None):
    fmt = '{}:{}: {}: {}\n'.format
    return fmt(filename, lineno, category.__name__, message)


warnings.formatwarning = warning_format


class PlotnineError(Exception):
    """
    Exception for ggplot errors
    """
    def __init__(self, *args):
        args = [dedent(arg) for arg in args]
        self.message = " ".join(args)

    def __str__(self):
        return repr(self.message)


class PlotnineWarning(UserWarning):
    """
    Warnings for ggplot inconsistencies
    """
    pass

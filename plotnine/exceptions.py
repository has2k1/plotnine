from __future__ import annotations
from textwrap import dedent
import warnings


# Show the warnings on one line, leaving out any code makes the
# message clear
def warning_format(  # type: ignore
    message, category, filename, lineno, line=None
):
    """
    Format for plotnine warnings
    """
    fmt = '{}:{}: {}: {}\n'.format
    return fmt(filename, lineno, category.__name__, message)


warnings.formatwarning = warning_format


class PlotnineError(Exception):
    """
    Exception for ggplot errors
    """

    def __init__(self, *args: str) -> None:
        args = [dedent(arg) for arg in args]
        self.message = " ".join(args)

    def __str__(self) -> str:
        """
        Error Message
        """
        return repr(self.message)


class PlotnineWarning(UserWarning):
    """
    Warnings for ggplot inconsistencies
    """
    pass

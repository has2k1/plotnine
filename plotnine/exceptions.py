from __future__ import annotations

import warnings
from textwrap import dedent
from typing import Optional, Type, Union


# Show the warnings on one line, leaving out any code makes the
# message clear
def warning_format(
    message: Union[Warning, str],
    category: Type[Warning],
    filename: str,
    lineno: int,
    line: Optional[str] = None,
) -> str:
    """
    Format for plotnine warnings
    """
    fmt = "{}:{}: {}: {}\n".format
    return fmt(filename, lineno, category.__name__, message)


warnings.formatwarning = warning_format


class PlotnineError(Exception):
    """
    Exception for ggplot errors
    """

    def __init__(self, *args: str):
        args = tuple(dedent(arg) for arg in args)
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

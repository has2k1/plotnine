from __future__ import annotations

import functools
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


def deprecated_themeable_name(cls):
    """
    Decorator to deprecate the name of a themeable
    """
    old_init = cls.__init__

    @functools.wraps(cls.__init__)
    def new_init(self, *args, **kwargs):
        old_name = cls.__name__
        new_name = cls.mro()[1].__name__
        msg = (
            f"\nThemeable '{old_name}' has been renamed to '{new_name}'.\n"
            f"'{old_name}' is now deprecated and will be removed in "
            "a future release."
        )
        warnings.warn(msg, category=FutureWarning, stacklevel=4)
        old_init(self, *args, **kwargs)

    cls.__init__ = new_init
    return cls

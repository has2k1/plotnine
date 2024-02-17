from __future__ import annotations

import sys
from enum import Enum
from typing import Optional

RESET = "\033[0m"


class Fg(Enum):
    """
    Foreground color codes
    """

    black = "\033[30m"
    red = "\033[31m"
    green = "\033[32m"
    orange = "\033[33m"
    blue = "\033[34m"
    purple = "\033[35m"
    cyan = "\033[36m"
    lightgrey = "\033[37m"
    darkgrey = "\033[90m"
    lightred = "\033[91m"
    lightgreen = "\033[92m"
    yellow = "\033[93m"
    lightblue = "\033[94m"
    pink = "\033[95m"
    lightcyan = "\033[96m"


class Bg(Enum):
    """
    Background color codes
    """

    black = "\033[40m"
    red = "\033[41m"
    green = "\033[42m"
    orange = "\033[43m"
    blue = "\033[44m"
    purple = "\033[45m"
    cyan = "\033[46m"
    lightgrey = "\033[47m"


class Effect(Enum):
    """
    Text effect codes
    """

    bold = "\033[01m"
    dim = "\033[02m"
    underline = "\033[04m"
    blink = "\033[05m"
    reverse = "\033[07m"  # bg & fg are reversed
    hide = "\033[08m"
    strikethrough = "\033[09m"


def T(
    s: str,
    fg: Optional[str] = None,
    bg: Optional[str] = None,
    effect: Optional[str] = None,
) -> str:
    """
    Enclose text string with ANSI codes

    e.g.
        # Red text
        T("sample", "red")

        # Red on lightgrey background
        T("sample", "red", "lightgrey")

        # Red on lightgrey background and underlined
        T("sample", "red", "lightgrey", "underlined")

        # Red underlined text
        T("sample", effect="underlined")

        # Red & bold underlined text
        T("sample", effect="bold, underlined")
    """

    def get(Ecls, prop_name) -> str:
        return getattr(Ecls, prop_name).value if prop_name else ""

    _fg = get(Fg, fg)
    _bg = get(Bg, bg)
    if effect:
        _effect = "".join(get(Effect, e.strip()) for e in effect.split(","))
    else:
        _effect = ""

    _reset = RESET if any((_fg, _bg, _effect)) else ""
    return f"{_fg}{_bg}{_effect}{s}{_reset}"


def T0(s: str, *args, **kwargs) -> str:
    """
    Enclose text string with ANSI codes if output is TTY
    """
    if sys.stdout.isatty():
        return T(s, *args, **kwargs)
    return s

from typing import Any

#: Development flag, e.g. set to ``True`` to prevent
#: the queuing up of figures when errors happen.
close_all_figures = False

#: Theme used when none is added to the ggplot object
current_theme = None

#: The base font family for all text that is part of the theme.
#: Default is sans-serif and one is choosen automatically from
#: rcParams["font.san-serif"]
base_family = "sans-serif"

#: Default aspect ratio used by the themes
aspect_ratio = "auto"

#: Default DPI used by the themes
dpi = 100

#: Default figure size inches
figure_size = (640 / dpi, 480 / dpi)

#: A size that is proportional of the figure width and
#: is used by some themes to determine other margins
base_margin = 0.01


def get_option(name: str) -> Any:
    """
    Get package option

    Parameters
    ----------
    name : str
        Name of the option
    """
    d = globals()

    if name in {"get_option", "set_option"} or name not in d:
        from .exceptions import PlotnineError

        raise PlotnineError(f"Unknown option {name}")

    return d[name]


def set_option(name: str, value: Any) -> Any:
    """
    Set package option

    Parameters
    ----------
    name : str
        Name of the option
    value : object
        New value of the option

    Returns
    -------
    old : object
        Old value of the option
    """
    d = globals()

    if name in {"get_option", "set_option"} or name not in d:
        from .exceptions import PlotnineError

        raise PlotnineError(f"Unknown option {name}")

    old = d[name]
    d[name] = value
    return old

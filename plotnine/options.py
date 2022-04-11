#: Development flag, e.g. set to ``True`` to prevent
#: the queuing up of figures when errors happen.
close_all_figures = False

#: Theme used when none is added to the ggplot object
current_theme = None

#: The base font family for all text that is part of
#: the theme
base_family = 'Dejavu Sans'

#: Default aspect ratio used by the themes
aspect_ratio = 'auto'

#: Default DPI used by the themes
dpi = 100

#: Default figure size inches
figure_size = (640/dpi, 480/dpi)

#: Default parameters for how to tune the subplot layout
# Choosen to match MPL 2.0 defaults
SUBPLOTS_ADJUST = {
    'left': 0.125,  # the left side of the subplots of the figure
    'right': 0.9,  # the right side of the subplots of the figure
    'bottom': 0.11,  # the bottom of the subplots of the figure
    'top': 0.88,  # the top of the subplots of the figure
}


def get_option(name):
    """
    Get package option

    Parameters
    ----------
    name : str
        Name of the option
    """
    d = globals()

    if name in {'get_option', 'set_option'} or name not in d:
        from ..exceptions import PlotnineError
        raise PlotnineError(f"Unknown option {name}")

    return d[name]


def set_option(name, value):
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

    if name in {'get_option', 'set_option'} or name not in d:
        from ..exceptions import PlotnineError
        raise PlotnineError(f"Unknown option {name}")

    old = d[name]
    d[name] = value
    return old

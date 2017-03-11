#: Development flag, e.g. set to ``True`` to prevent
#: the queuing up of figures when errors happen.
close_all_figures = False

#: Theme used when none is added to the ggplot object
current_theme = None

#: Default aspect ratio used by the themes
aspect_ratio = None

#: Default DPI used by the themes
dpi = 100

#: Default figure size inches
figure_size = (640/dpi, 480/dpi)


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
        raise PlotnineError("Unknown option {}".format(name))

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
        raise PlotnineError("Unknown option {}".format(name))

    old = d[name]
    d[name] = value
    return old

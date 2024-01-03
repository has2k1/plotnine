# type: ignore

"""Functions that alter the matplotlib rc dictionary on the fly."""


import functools

import matplotlib as _mpl

# https://github.com/mwaskom/seaborn/blob/master/seaborn/rcmod.py
# License: BSD-3-Clause License
#
# Modifications
# ---------------
# modified set_theme()
# removed set_palette(), reset_defaults(), reset_orig()
#
# We (plotnine) do not want to modify the rcParams
# on the matplotlib instance, so we create a dummy object
# The set_* function work on the rcParams dict on that
# object and then set() returns it. Then outside this
# file we only need to call the set() function.


class dummy:
    """
    No Op
    """

    __version__ = _mpl.__version__
    rcParams = {}


mpl = dummy()


_style_keys = [
    "axes.facecolor",
    "axes.edgecolor",
    "axes.grid",
    "axes.axisbelow",
    "axes.labelcolor",
    "figure.facecolor",
    "grid.color",
    "grid.linestyle",
    "text.color",
    "xtick.color",
    "ytick.color",
    "xtick.direction",
    "ytick.direction",
    "lines.solid_capstyle",
    "patch.edgecolor",
    "patch.force_edgecolor",
    "image.cmap",
    "font.family",
    "font.sans-serif",
    "xtick.bottom",
    "xtick.top",
    "ytick.left",
    "ytick.right",
    "axes.spines.left",
    "axes.spines.bottom",
    "axes.spines.right",
    "axes.spines.top",
]

_context_keys = [
    "font.size",
    "axes.labelsize",
    "axes.titlesize",
    "xtick.labelsize",
    "ytick.labelsize",
    "legend.fontsize",
    "legend.title_fontsize",
    "axes.linewidth",
    "grid.linewidth",
    "lines.linewidth",
    "lines.markersize",
    "patch.linewidth",
    "xtick.major.width",
    "ytick.major.width",
    "xtick.minor.width",
    "ytick.minor.width",
    "xtick.major.size",
    "ytick.major.size",
    "xtick.minor.size",
    "ytick.minor.size",
]


def set_theme(
    context="notebook",
    style="darkgrid",
    palette="deep",
    font="sans-serif",
    font_scale=1,
    color_codes=False,
    rc=None,
):
    """
    Set aesthetic parameters in one step

    Each set of parameters can be set directly or temporarily, see the
    referenced functions below for more information.

    Parameters
    ----------
    context : string or dict
        Plotting context parameters, see :func:`plotting_context`
    style : string or dict
        Axes style parameters, see :func:`axes_style`
    palette : string or sequence
        Color palette, see :func:`color_palette`
    font : string
        Font family, see matplotlib font manager.
    font_scale : float
        Separate scaling factor to independently scale the size of the
        font elements.
    color_codes : bool
        If `True` and `palette` is a seaborn palette, remap the shorthand
        color codes (e.g. "b", "g", "r", etc.) to the colors from this palette.
    rc : dict or None
        Dictionary of rc parameter mappings to override the above.

    """
    set_context(context, font_scale)
    set_style(style, rc={"font.family": font})
    if rc is not None:
        mpl.rcParams.update(rc)
    return mpl.rcParams


def set(*args, **kwargs):
    """
    Alias for :func:`set_theme`, which is the preferred interface

    This function may be removed in the future.
    """
    set_theme(*args, **kwargs)


def axes_style(style=None, rc=None):
    """
    Return a parameter dict for the aesthetic style of the plots

    This affects things like the color of the axes, whether a grid is
    enabled by default, and other aesthetic elements.

    This function returns an object that can be used in a `with` statement
    to temporarily change the style parameters.

    Parameters
    ----------
    style : "darkgrid" | "whitegrid" | "dark" | "white" | "ticks" | dict | None
        A dictionary of parameters or the name of a preconfigured set.
    rc : dict
        Parameter mappings to override the values in the preset seaborn
        style dictionaries. This only updates parameters that are
        considered part of the style definition.

    Examples
    --------
    >>> st = axes_style("whitegrid")

    >>> set_style("ticks", {"xtick.major.size": 8, "ytick.major.size": 8})

    >>> import matplotlib.pyplot as plt
    >>> with axes_style("white"):
    ...     f, ax = plt.subplots()
    ...     ax.plot(x, y)               # doctest: +SKIP

    See Also
    --------
    set_style : set the matplotlib parameters for a seaborn theme
    plotting_context : return a parameter dict to to scale plot elements
    color_palette : define the color palette for a plot

    """
    if style is None:
        style_dict = {k: mpl.rcParams[k] for k in _style_keys}

    elif isinstance(style, dict):
        style_dict = style

    else:
        styles = ["white", "dark", "whitegrid", "darkgrid", "ticks"]
        if style not in styles:
            raise ValueError(f"style must be one of {', '.join(styles)}")

        # Define colors here
        dark_gray = ".15"
        light_gray = ".8"

        # Common parameters
        style_dict = {
            "figure.facecolor": "white",
            "axes.labelcolor": dark_gray,
            "xtick.direction": "out",
            "ytick.direction": "out",
            "xtick.color": dark_gray,
            "ytick.color": dark_gray,
            "axes.axisbelow": True,
            "grid.linestyle": "-",
            "text.color": dark_gray,
            "font.family": ["sans-serif"],
            "font.sans-serif": [
                "Arial",
                "DejaVu Sans",
                "Liberation Sans",
                "Bitstream Vera Sans",
                "sans-serif",
            ],
            "lines.solid_capstyle": "round",
            "patch.edgecolor": "w",
            "patch.force_edgecolor": True,
            "image.cmap": "Greys",
            "xtick.top": False,
            "ytick.right": False,
        }

        # Set grid on or off
        if "grid" in style:
            style_dict.update(
                {
                    "axes.grid": True,
                }
            )
        else:
            style_dict.update(
                {
                    "axes.grid": False,
                }
            )

        # Set the color of the background, spines, and grids
        if style.startswith("dark"):
            style_dict.update(
                {
                    "axes.facecolor": "#EAEAF2",
                    "axes.edgecolor": "white",
                    "grid.color": "white",
                    "axes.spines.left": True,
                    "axes.spines.bottom": True,
                    "axes.spines.right": True,
                    "axes.spines.top": True,
                }
            )

        elif style == "whitegrid":
            style_dict.update(
                {
                    "axes.facecolor": "white",
                    "axes.edgecolor": light_gray,
                    "grid.color": light_gray,
                    "axes.spines.left": True,
                    "axes.spines.bottom": True,
                    "axes.spines.right": True,
                    "axes.spines.top": True,
                }
            )

        elif style in ["white", "ticks"]:
            style_dict.update(
                {
                    "axes.facecolor": "white",
                    "axes.edgecolor": dark_gray,
                    "grid.color": light_gray,
                    "axes.spines.left": True,
                    "axes.spines.bottom": True,
                    "axes.spines.right": True,
                    "axes.spines.top": True,
                }
            )

        # Show or hide the axes ticks
        if style == "ticks":
            style_dict.update(
                {
                    "xtick.bottom": True,
                    "ytick.left": True,
                }
            )
        else:
            style_dict.update(
                {
                    "xtick.bottom": False,
                    "ytick.left": False,
                }
            )

    # Remove entries that are not defined in the base list of valid keys
    # This lets us handle matplotlib <=/> 2.0
    style_dict = {k: v for k, v in style_dict.items() if k in _style_keys}

    # Override these settings with the provided rc dictionary
    if rc is not None:
        rc = {k: v for k, v in rc.items() if k in _style_keys}
        style_dict.update(rc)

    # Wrap in an _AxesStyle object so this can be used in a with statement
    style_object = _AxesStyle(style_dict)

    return style_object


def set_style(style=None, rc=None):
    """
    Set the aesthetic style of the plots

    This affects things like the color of the axes, whether a grid is
    enabled by default, and other aesthetic elements.

    Parameters
    ----------
    style : "darkgrid" | "whitegrid" | "dark" | "white" | "ticks" | dict | None
        A dictionary of parameters or the name of a preconfigured set.
    rc : dict
        Parameter mappings to override the values in the preset seaborn
        style dictionaries. This only updates parameters that are
        considered part of the style definition.

    Examples
    --------
    >>> set_style("whitegrid")

    >>> set_style("ticks", {"xtick.major.size": 8, "ytick.major.size": 8})

    See Also
    --------
    axes_style : return a dict of parameters or use in a `with` statement
                 to temporarily set the style.
    set_context : set parameters to scale plot elements
    set_palette : set the default color palette for figures

    """
    style_object = axes_style(style, rc)
    mpl.rcParams.update(style_object)


def plotting_context(context=None, font_scale=1, rc=None):
    """
    Return a parameter dict to scale elements of the figure

    This affects things like the size of the labels, lines, and other
    elements of the plot, but not the overall style. The base context
    is "notebook", and the other contexts are "paper", "talk", and "poster",
    which are version of the notebook parameters scaled by .8, 1.3, and 1.6,
    respectively.

    This function returns an object that can be used in a `with` statement
    to temporarily change the context parameters.

    Parameters
    ----------
    context : dict, None, or one of {paper, notebook, talk, poster}
        A dictionary of parameters or the name of a preconfigured set.
    font_scale : float, optional
        Separate scaling factor to independently scale the size of the
        font elements.
    rc : dict, optional
        Parameter mappings to override the values in the preset seaborn
        context dictionaries. This only updates parameters that are
        considered part of the context definition.

    Examples
    --------
    >>> c = plotting_context("poster")

    >>> c = plotting_context("notebook", font_scale=1.5)

    >>> c = plotting_context("talk", rc={"lines.linewidth": 2})

    >>> import matplotlib.pyplot as plt
    >>> with plotting_context("paper"):
    ...     f, ax = plt.subplots()
    ...     ax.plot(x, y)                 # doctest: +SKIP

    See Also
    --------
    set_context : set the matplotlib parameters to scale plot elements
    axes_style : return a dict of parameters defining a figure style
    color_palette : define the color palette for a plot
    """
    if context is None:
        context_dict = {k: mpl.rcParams[k] for k in _context_keys}

    elif isinstance(context, dict):
        context_dict = context

    else:
        contexts = ["paper", "notebook", "talk", "poster"]
        if context not in contexts:
            raise ValueError(f"context must be in {', '.join(contexts)}")

        # Set up dictionary of default parameters
        texts_base_context = {
            "font.size": 12,
            "axes.labelsize": 12,
            "axes.titlesize": 12,
            "xtick.labelsize": 11,
            "ytick.labelsize": 11,
            "legend.fontsize": 11,
            "legend.title_fontsize": 12,
        }

        base_context = {
            "axes.linewidth": 1.25,
            "grid.linewidth": 1,
            "lines.linewidth": 1.5,
            "lines.markersize": 6,
            "patch.linewidth": 1,
            "xtick.major.width": 1.25,
            "ytick.major.width": 1.25,
            "xtick.minor.width": 1,
            "ytick.minor.width": 1,
            "xtick.major.size": 6,
            "ytick.major.size": 6,
            "xtick.minor.size": 4,
            "ytick.minor.size": 4,
        }
        base_context.update(texts_base_context)

        # Scale all the parameters by the same factor depending on the context
        scaling = {"paper": 0.8, "notebook": 1, "talk": 1.5, "poster": 2}[
            context
        ]
        context_dict = {k: v * scaling for k, v in base_context.items()}

        # Now independently scale the fonts
        font_keys = texts_base_context.keys()
        font_dict = {k: context_dict[k] * font_scale for k in font_keys}
        context_dict.update(font_dict)

    # Override these settings with the provided rc dictionary
    if rc is not None:
        rc = {k: v for k, v in rc.items() if k in _context_keys}
        context_dict.update(rc)

    # Wrap in a _PlottingContext object so this can be used in a with statement
    context_object = _PlottingContext(context_dict)

    return context_object


def set_context(context=None, font_scale=1, rc=None):
    """
    Set the plotting context parameters

    This affects things like the size of the labels, lines, and other
    elements of the plot, but not the overall style. The base context
    is "notebook", and the other contexts are "paper", "talk", and "poster",
    which are version of the notebook parameters scaled by .8, 1.3, and 1.6,
    respectively.

    Parameters
    ----------
    context : dict, None, or one of {paper, notebook, talk, poster}
        A dictionary of parameters or the name of a preconfigured set.
    font_scale : float, optional
        Separate scaling factor to independently scale the size of the
        font elements.
    rc : dict, optional
        Parameter mappings to override the values in the preset seaborn
        context dictionaries. This only updates parameters that are
        considered part of the context definition.

    Examples
    --------
    >>> set_context("paper")

    >>> set_context("talk", font_scale=1.4)

    >>> set_context("talk", rc={"lines.linewidth": 2})

    See Also
    --------
    plotting_context : return a dictionary of rc parameters, or use in
                       a `with` statement to temporarily set the context.
    set_style : set the default parameters for figure style
    set_palette : set the default color palette for figures

    """
    context_object = plotting_context(context, font_scale, rc)
    mpl.rcParams.update(context_object)


class _RCAesthetics(dict):
    def __enter__(self):
        rc = mpl.rcParams
        self._orig = {k: rc[k] for k in self._keys}
        self._set(self)

    def __exit__(self, exc_type, exc_value, exc_tb):
        self._set(self._orig)

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with self:
                return func(*args, **kwargs)

        return wrapper


class _AxesStyle(_RCAesthetics):
    """Light wrapper on a dict to set style temporarily."""

    _keys = _style_keys
    _set = staticmethod(set_style)


class _PlottingContext(_RCAesthetics):
    """Light wrapper on a dict to set context temporarily."""

    _keys = _context_keys
    _set = staticmethod(set_context)

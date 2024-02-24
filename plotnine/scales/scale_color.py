from __future__ import annotations

import typing
from warnings import warn

from .._utils.registry import alias
from ..doctools import document
from ..exceptions import PlotnineWarning
from .scale_continuous import scale_continuous
from .scale_datetime import scale_datetime
from .scale_discrete import scale_discrete

if typing.TYPE_CHECKING:
    from typing import Literal, Optional, Sequence

    from mizani.typing import ColorScheme, ColorSchemeShort


# Discrete color scales #
# Note: plotnine operates in the hcl space
@document
class scale_color_hue(scale_discrete):
    """
    Qualitative color scale with evenly spaced hues

    Parameters
    ----------
    h :
        first hue. Must be in the range [0, 1]
    l :
        lightness. Must be in the range [0, 1]
    s :
        saturation. Must be in the range [0, 1]
    colorspace :
        Color space to use. Should be one of
        [hls](https://en.wikipedia.org/wiki/HSL_and_HSV)
        or
        [husl](http://www.husl-colors.org/).
    {superclass_parameters}
    na_value : str, default="#7F7F7F"
        Color of missing values.
    """

    _aesthetics = ["color"]
    na_value = "#7F7F7F"

    def __init__(
        self,
        h: float = 0.01,
        l: float = 0.6,
        s: float = 0.65,
        color_space: Literal["hls", "husl"] = "hls",
        **kwargs,
    ):
        from mizani.palettes import hue_pal

        self._palette = hue_pal(h, l, s, color_space=color_space)
        scale_discrete.__init__(self, **kwargs)


@document
class scale_fill_hue(scale_color_hue):
    """
    Qualitative color scale with evenly spaced hues

    Parameters
    ----------
    {superclass_parameters}
    """

    _aesthetics = ["fill"]


@document
class scale_color_brewer(scale_discrete):
    """
    Sequential, diverging and qualitative discrete color scales

    See `colorbrewer.org <http://colorbrewer2.org/>`_

    Parameters
    ----------
    type :
        Type of data. Sequential, diverging or qualitative
    palette : int | str, default=1
         If a string, will use that named palette.
         If a number, will index into the list of palettes
         of appropriate type.
    direction: 1 | -1, default=1
         Sets the order of colors in the scale. If 1, colors are
         as output by [](`~mizani.palettes.brewer_pal`). If -1,
         the order of colors is reversed.
    {superclass_parameters}
    na_value : str, default="#7F7F7F"
        Color of missing values.
    """

    _aesthetics = ["color"]
    na_value = "#7F7F7F"

    def __init__(
        self,
        type: ColorScheme | ColorSchemeShort = "seq",
        palette: int | str = 1,
        direction: Literal[1, -1] = 1,
        **kwargs,
    ):
        from mizani.palettes import brewer_pal

        self._palette = brewer_pal(type, palette, direction=direction)
        scale_discrete.__init__(self, **kwargs)


@document
class scale_fill_brewer(scale_color_brewer):
    """
    Sequential, diverging and qualitative color scales

    Parameters
    ----------
    {superclass_parameters}
    """

    _aesthetics = ["fill"]


@document
class scale_color_grey(scale_discrete):
    """
    Sequential grey color scale.

    Parameters
    ----------
    start : float, default=0.2
        grey value at low end of palette.
    end : float, default=0.8
        grey value at high end of palette
    {superclass_parameters}
    """

    _aesthetics = ["color"]

    def __init__(self, start=0.2, end=0.8, **kwargs):
        from mizani.palettes import grey_pal

        self._palette = grey_pal(start, end)
        scale_discrete.__init__(self, **kwargs)


@document
class scale_fill_grey(scale_color_grey):
    """
    Sequential grey color scale.

    Parameters
    ----------
    {superclass_parameters}
    """

    _aesthetics = ["fill"]


# Continuous color scales #


@document
class scale_color_gradient(scale_continuous):
    """
    Create a 2 point color gradient

    Parameters
    ----------
    low : str
        low color
    high : str
        high color
    {superclass_parameters}
    na_value : str, default="#7F7F7F"
        Color of missing values.

    See Also
    --------
    plotnine.scale_color_gradient2
    plotnine.scale_color_gradientn
    """

    _aesthetics = ["color"]
    guide = "colorbar"
    na_value = "#7F7F7F"

    def __init__(self, low="#132B43", high="#56B1F7", **kwargs):
        """
        Create colormap that will be used by the palette
        """
        from mizani.palettes import gradient_n_pal

        self._palette = gradient_n_pal([low, high])
        scale_continuous.__init__(self, **kwargs)


@document
class scale_fill_gradient(scale_color_gradient):
    """
    Create a 2 point color gradient

    Parameters
    ----------
    {superclass_parameters}
    """

    _aesthetics = ["fill"]


@document
class scale_color_desaturate(scale_continuous):
    """
    Create a desaturated color gradient

    Parameters
    ----------
    color : str, default="red"
        Color to desaturate
    prop : float, default=0
        Saturation channel of color will be multiplied by
        this value.
    reverse : bool, default=False
        Whether to go from color to desaturated color
        or desaturated color to color.
    {superclass_parameters}
    na_value : str, default="#7F7F7F"
        Color of missing values.
    """

    _aesthetics = ["color"]
    guide = "colorbar"
    na_value = "#7F7F7F"

    def __init__(self, color="red", prop=0, reverse=False, **kwargs):
        from mizani.palettes import desaturate_pal

        # TODO: fix types in mizani
        self.palette = desaturate_pal(color, prop, reverse)  # pyright: ignore
        scale_continuous.__init__(self, **kwargs)


@document
class scale_fill_desaturate(scale_color_desaturate):
    """
    Create a desaturated color gradient

    Parameters
    ----------
    {superclass_parameters}
    """

    _aesthetics = ["fill"]


@document
class scale_color_gradient2(scale_continuous):
    """
    Create a 3 point diverging color gradient

    Parameters
    ----------
    low : str
        low color
    mid : str
        mid point color
    high : str
        high color
    midpoint : float, default=0
        Mid point of the input data range.
    {superclass_parameters}
    na_value : str, default="#7F7F7F"
        Color of missing values

    See Also
    --------
    plotnine.scale_color_gradient
    plotnine.scale_color_gradientn
    """

    _aesthetics = ["color"]
    guide = "colorbar"
    na_value = "#7F7F7F"

    def __init__(
        self,
        low="#832424",
        mid="#FFFFFF",
        high="#3A3A98",
        midpoint=0,
        **kwargs,
    ):
        from mizani.bounds import rescale_mid
        from mizani.palettes import gradient_n_pal

        # All rescale functions should have the same signature
        def _rescale_mid(*args, **kwargs):
            return rescale_mid(*args, mid=midpoint, **kwargs)

        kwargs["rescaler"] = _rescale_mid
        # TODO: fix types in mizani
        self.palette = gradient_n_pal([low, mid, high])  # pyright: ignore
        scale_continuous.__init__(self, **kwargs)


@document
class scale_fill_gradient2(scale_color_gradient2):
    """
    Create a 3 point diverging color gradient

    Parameters
    ----------
    {superclass_parameters}
    """

    _aesthetics = ["fill"]


@document
class scale_color_gradientn(scale_continuous):
    """
    Create a n color gradient

    Parameters
    ----------
    colors : list
        list of colors
    values : list, default=None
        list of points in the range [0, 1] at which to
        place each color. Must be the same size as
        `colors`. Default to evenly space the colors
    {superclass_parameters}
    na_value : str, default="#7F7F7F"
        Color of missing values

    See Also
    --------
    plotnine.scale_color_gradient
    plotnine.scale_color_gradientn
    """

    _aesthetics = ["color"]
    guide = "colorbar"
    na_value = "#7F7F7F"

    def __init__(self, colors, values=None, **kwargs):
        from mizani.palettes import gradient_n_pal

        # TODO: fix types in mizani
        self.palette = gradient_n_pal(colors, values)  # pyright: ignore
        scale_continuous.__init__(self, **kwargs)


@document
class scale_fill_gradientn(scale_color_gradientn):
    """
    Create a n color gradient

    Parameters
    ----------
    {superclass_parameters}
    """

    _aesthetics = ["fill"]


@document
class scale_color_distiller(scale_color_gradientn):
    """
    Sequential and diverging continuous color scales

    This is a convinience scale around
    [](`~plotnine.scales.scale_color_gradientn`) with colors from
    [colorbrewer.org](http://colorbrewer2.org). It smoothly
    interpolates 7 colors from a brewer palette to create a
    continuous palette.

    Parameters
    ----------
    type :
        Type of data. Sequential, diverging or qualitative
    palette :
         If a string, will use that named palette.
         If a number, will index into the list of palettes
         of appropriate type. Default is 1
    values :
        list of points in the range [0, 1] at which to
        place each color. Must be the same size as
        `colors`. Default to evenly space the colors
    direction :
        Sets the order of colors in the scale. If 1
        colors are as output by [](`~mizani.palettes.brewer_pal`).
        If -1, the order of colors is reversed.
    {superclass_parameters}
    na_value : str, default="#7F7F7F"
        Color of missing values.
    """

    _aesthetics = ["color"]
    guide = "colorbar"
    na_value = "#7F7F7F"

    def __init__(
        self,
        type: ColorScheme | ColorSchemeShort = "seq",
        palette: int | str = 1,
        values: Optional[Sequence[float]] = None,
        direction: Literal[1, -1] = -1,
        **kwargs,
    ):
        """
        Create colormap that will be used by the palette
        """
        from mizani.palettes import brewer_pal

        if type.lower() in ("qual", "qualitative"):
            warn(
                "Using a discrete color palette in a continuous scale."
                "Consider using type = 'seq' or type = 'div' instead",
                PlotnineWarning,
            )

        # Grab 7 colors from brewer and create a gradient palette
        # An odd number matches the midpoint of the palette to that
        # of the data
        colors = brewer_pal(type, palette, direction=direction)(7)
        scale_color_gradientn.__init__(self, colors, values, **kwargs)


@document
class scale_fill_distiller(scale_color_distiller):
    """
    Sequential, diverging continuous color scales

    Parameters
    ----------
    {superclass_parameters}
    """

    _aesthetics = ["fill"]


# matplotlib colormaps
@document
class scale_color_cmap(scale_continuous):
    """
    Create color scales using Matplotlib colormaps

    Parameters
    ----------
    cmap_name :
        A standard Matplotlib colormap name. The default is
        `viridis`. For the list of names checkout the output
        of `matplotlib.cm.cmap_d.keys()` or see the
        `documentation <http://matplotlib.org/users/colormaps.html>`_.
    {superclass_parameters}
    na_value : str, default="#7F7F7F"
        Color of missing values.

    See Also
    --------
    [](`matplotlib.cm`)
    [](`matplotlib.colors`)
    """

    _aesthetics = ["color"]
    guide = "colorbar"
    na_value = "#7F7F7F"

    def __init__(self, cmap_name: str = "viridis", **kwargs):
        from mizani.palettes import cmap_pal

        # TODO: fix types in mizani
        self.palette = cmap_pal(cmap_name)  # pyright: ignore
        super().__init__(**kwargs)


@document
class scale_fill_cmap(scale_color_cmap):
    """
    Create color scales using Matplotlib colormaps

    Parameters
    ----------
    {superclass_parameters}
    """

    _aesthetics = ["fill"]


@document
class scale_color_cmap_d(scale_discrete):
    """
    A discrete color scales using Matplotlib colormaps

    Parameters
    ----------
    cmap_name :
        A standard Matplotlib colormap name. It must be of type
        [](`matplotlib.colors.ListedColormap`).
        The default is `viridis`. For the list of names checkout
        the output of `matplotlib.cm.cmap_d.keys()` or see the
        `documentation <http://matplotlib.org/users/colormaps.html>`_.
    {superclass_parameters}
    na_value : str, default="#7F7F7F"
        Color of missing values.

    See Also
    --------
    [](`matplotlib.cm`)
    [](`matplotlib.colors`)
    """

    _aesthetics = ["color"]
    na_value = "#7F7F7F"

    def __init__(self, cmap_name: str = "viridis", **kwargs):
        from mizani.palettes import cmap_d_pal

        self._palette = cmap_d_pal(cmap_name)
        super().__init__(**kwargs)


@document
class scale_fill_cmap_d(scale_color_cmap_d):
    """
    Create color scales using Matplotlib colormaps

    Parameters
    ----------
    {superclass_parameters}
    """

    _aesthetics = ["fill"]


@document
class scale_color_datetime(scale_datetime, scale_color_cmap):
    """
    Datetime color scale

    Parameters
    ----------
    {superclass_parameters}
    """


@document
class scale_fill_datetime(scale_datetime, scale_fill_cmap):
    """
    Datetime fill scale

    Parameters
    ----------
    {superclass_parameters}
    """


# Default scales
@alias
class scale_color_discrete(scale_color_hue):
    pass


@alias
class scale_color_continuous(scale_color_cmap):
    pass


@alias
class scale_color_ordinal(scale_color_cmap_d):
    pass


@alias
class scale_fill_discrete(scale_fill_hue):
    pass


@alias
class scale_fill_continuous(scale_fill_cmap):
    pass


@alias
class scale_fill_ordinal(scale_fill_cmap_d):
    pass


# American to British spelling
@alias
class scale_colour_hue(scale_color_hue):
    pass


@alias
class scale_color_gray(scale_color_grey):
    pass


@alias
class scale_colour_grey(scale_color_grey):
    pass


@alias
class scale_colour_gray(scale_color_grey):
    pass


@alias
class scale_fill_gray(scale_fill_grey):
    pass


@alias
class scale_colour_brewer(scale_color_brewer):
    pass


@alias
class scale_colour_desaturate(scale_color_desaturate):
    pass


@alias
class scale_colour_gradient(scale_color_gradient):
    pass


@alias
class scale_colour_gradient2(scale_color_gradient2):
    pass


@alias
class scale_colour_gradientn(scale_color_gradientn):
    pass


@alias
class scale_colour_discrete(scale_color_hue):
    pass


@alias
class scale_colour_continuous(scale_color_cmap):
    pass


@alias
class scale_colour_distiller(scale_color_distiller):
    pass


@alias
class scale_colour_cmap(scale_color_cmap):
    pass


@alias
class scale_colour_cmap_d(scale_color_cmap_d):
    pass


@alias
class scale_colour_datetime(scale_color_datetime):
    pass


@alias
class scale_colour_ordinal(scale_color_cmap_d):
    pass

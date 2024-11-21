from __future__ import annotations

from dataclasses import KW_ONLY, InitVar, dataclass
from typing import Literal, Sequence
from warnings import warn

from .._utils.registry import alias
from ..exceptions import PlotnineWarning
from .scale_continuous import scale_continuous
from .scale_datetime import scale_datetime
from .scale_discrete import scale_discrete


@dataclass
class _scale_color_discrete(scale_discrete):
    """
    Base class for all discrete color scales
    """

    _aesthetics = ["color"]
    _: KW_ONLY
    na_value: str = "#7F7F7F"
    """
    Color of missing values.
    """


@dataclass
class _scale_color_continuous(
    scale_continuous[Literal["legend", "colorbar"] | None],
):
    """
    Base class for all continuous color scales
    """

    _aesthetics = ["color"]
    _: KW_ONLY
    guide: Literal["legend", "colorbar"] | None = "colorbar"
    na_value: str = "#7F7F7F"
    """
    Color of missing values.
    """


# Discrete color scales #
# Note: plotnine operates in the hcl space
@dataclass
class scale_color_hue(_scale_color_discrete):
    """
    Qualitative color scale with evenly spaced hues
    """

    h: InitVar[float] = 0.01
    """
    Hue. Must be in the range [0, 1]
    """

    l: InitVar[float] = 0.6
    """
    Lightness. Must be in the range [0, 1]
    """

    s: InitVar[float] = 0.65
    """
    Saturation. Must be in the range [0, 1]
    """

    color_space: InitVar[Literal["hls", "hsluv"]] = "hls"
    """
    Color space to use. Should be one of
    [hls](https://en.wikipedia.org/wiki/HSL_and_HSV)
    or [hsluv](https://www.hsluv.org/).
    https://www.hsluv.org/
    """

    def __post_init__(self, h, l, s, color_space):
        from mizani.palettes import hue_pal

        super().__post_init__()
        self.palette = hue_pal(h, l, s, color_space=color_space)


@dataclass
class scale_fill_hue(scale_color_hue):
    """
    Qualitative color scale with evenly spaced hues
    """

    _aesthetics = ["fill"]


@dataclass
class scale_color_brewer(_scale_color_discrete):
    """
    Sequential, diverging and qualitative discrete color scales

    See `colorbrewer.org <http://colorbrewer2.org/>`_
    """

    type: InitVar[
        Literal[
            "diverging",
            "qualitative",
            "sequential",
            "div",
            "qual",
            "seq",
        ]
    ] = "seq"
    """
    Type of data
    """

    palette: InitVar[int | str] = 1
    """
    If a string, will use that named palette. If a number, will index
    into the list of palettes of appropriate type.
    """

    direction: InitVar[Literal[1, -1]] = 1
    """
    Sets the order of colors in the scale. If 1, colors are as output
    [](`~mizani.palettes.brewer_pal`). If -1, the order of colors is
    reversed.
    """

    def __post_init__(self, type, palette, direction):
        from mizani.palettes import brewer_pal

        super().__post_init__()
        self.palette = brewer_pal(  # type: ignore
            type, palette, direction=direction
        )


@dataclass
class scale_fill_brewer(scale_color_brewer):
    """
    Sequential, diverging and qualitative color scales
    """

    _aesthetics = ["fill"]


@dataclass
class scale_color_grey(_scale_color_discrete):
    """
    Sequential grey color scale.
    """

    start: InitVar[float] = 0.2
    """
    Grey value at low end of palette.
    """

    end: InitVar[float] = 0.8
    """
    Grey value at high end of palette
    """

    _aesthetics = ["color"]

    def __post_init__(self, start, end):
        from mizani.palettes import grey_pal

        super().__post_init__()
        self.palette = grey_pal(start, end)


@dataclass
class scale_fill_grey(scale_color_grey):
    """
    Sequential grey color scale.
    """

    _aesthetics = ["fill"]


# Continuous color scales #


@dataclass
class scale_color_gradient(_scale_color_continuous):
    """
    Create a 2 point color gradient

    See Also
    --------
    plotnine.scale_color_gradient2
    plotnine.scale_color_gradientn
    """

    low: InitVar[str] = "#132B43"
    """
    Low color.
    """

    high: InitVar[str] = "#56B1F7"
    """
    High color.
    """

    def __post_init__(self, low, high):
        from mizani.palettes import gradient_n_pal

        super().__post_init__()
        self.palette = gradient_n_pal([low, high])


@dataclass
class scale_fill_gradient(scale_color_gradient):
    """
    Create a 2 point color gradient
    """

    _aesthetics = ["fill"]


@dataclass
class scale_color_desaturate(_scale_color_continuous):
    """
    Create a desaturated color gradient
    """

    color: InitVar[str] = "red"
    """
    Color to desaturate
    """

    prop: InitVar[float] = 0
    """
    Saturation channel of color will be multiplied by this value.
    """

    reverse: InitVar[bool] = False
    """
    Whether to go from color to desaturated color or desaturated color
    to color.
    """

    def __post_init__(self, color, prop, reverse):
        from mizani.palettes import desaturate_pal

        super().__post_init__()
        self.palette = desaturate_pal(color, prop, reverse)


@dataclass
class scale_fill_desaturate(scale_color_desaturate):
    """
    Create a desaturated color gradient
    """

    _aesthetics = ["fill"]


@dataclass
class scale_color_gradient2(_scale_color_continuous):
    """
    Create a 3 point diverging color gradient

    See Also
    --------
    plotnine.scale_color_gradient
    plotnine.scale_color_gradientn
    """

    low: InitVar[str] = "#832424"
    """
    Low color.
    """

    mid: InitVar[str] = "#FFFFFF"
    """
    Mid-point color.

    """
    high: InitVar[str] = "#3A3A98"
    """
    High color.
    """

    midpoint: InitVar[float] = 0
    """
    Mid point of the input data range.
    """

    def __post_init__(self, low, mid, high, midpoint):
        from mizani.bounds import rescale_mid
        from mizani.palettes import gradient_n_pal

        # All rescale functions should have the same signature
        def _rescale_mid(*args, **kwargs):
            return rescale_mid(*args, mid=midpoint, **kwargs)

        self.rescaler = _rescale_mid
        self.palette = gradient_n_pal([low, mid, high])
        super().__post_init__()


@dataclass
class scale_fill_gradient2(scale_color_gradient2):
    """
    Create a 3 point diverging color gradient
    """

    _aesthetics = ["fill"]


@dataclass
class scale_color_gradientn(_scale_color_continuous):
    """
    Create a n color gradient

    See Also
    --------
    plotnine.scale_color_gradient
    plotnine.scale_color_gradientn
    """

    colors: InitVar[Sequence[str]] = "#832424"
    """
    List of colors
    """

    values: InitVar[Sequence[float] | None] = None
    """
    list of points in the range [0, 1] at which to place each color.
    Must be the same size as `colors`. Default to evenly space the colors
    """

    def __post_init__(self, colors, values):
        from mizani.palettes import gradient_n_pal

        self.palette = gradient_n_pal(colors, values)
        super().__post_init__()


@dataclass
class scale_fill_gradientn(scale_color_gradientn):
    """
    Create a n color gradient
    """

    _aesthetics = ["fill"]


@dataclass
class scale_color_distiller(_scale_color_continuous):
    """
    Sequential and diverging continuous color scales

    This is a convenience scale around
    [](`~plotnine.scales.scale_color_gradientn`) with colors from
    [colorbrewer.org](http://colorbrewer2.org). It smoothly
    interpolates 7 colors from a brewer palette to create a
    continuous palette.
    """

    type: InitVar[
        Literal[
            "diverging",
            "qualitative",
            "sequential",
            "div",
            "qual",
            "seq",
        ]
    ] = "seq"
    """
    Type of data
    """

    palette: InitVar[int | str] = 1
    """
    If a string, will use that named palette. If a number, will index
    into the list of palettes of appropriate type.
    """

    values: InitVar[Sequence[float] | None] = None
    """
    List of points in the range [0, 1] at which to place each color.
    Must be the same size as `colors`. Default to evenly space the colors
    """

    direction: InitVar[Literal[1, -1]] = 1
    """
    Sets the order of colors in the scale. If 1, colors are as output
    [](`~mizani.palettes.brewer_pal`). If -1, the order of colors is
    reversed.
    """

    def __post_init__(self, type, palette, values, direction):
        """
        Create colormap that will be used by the palette
        """
        from mizani.palettes import brewer_pal, gradient_n_pal

        if type.lower() in ("qual", "qualitative"):
            warn(
                "Using a discrete color palette in a continuous scale."
                "Consider using type = 'seq' or type = 'div' instead",
                PlotnineWarning,
            )

        # Grab 7 colors from brewer and create a gradient palette
        # An odd number matches the midpoint of the palette to that
        # of the data
        super().__post_init__()
        colors = brewer_pal(type, palette, direction=direction)(7)
        self.palette = gradient_n_pal(colors, values)  # type: ignore


@dataclass
class scale_fill_distiller(scale_color_distiller):
    """
    Sequential, diverging continuous color scales
    """

    _aesthetics = ["fill"]


# matplotlib colormaps
@dataclass
class scale_color_cmap(_scale_color_continuous):
    """
    Create color scales using Matplotlib colormaps

    See Also
    --------
    [](`matplotlib.cm`)
    [](`matplotlib.colors`)
    """

    cmap_name: InitVar[str] = "viridis"
    """
    A standard Matplotlib colormap name. The default is `viridis`.
    For the list of names checkout the output of
    `matplotlib.cm.cmap_d.keys()` or see
    [colormaps](https://matplotlib.org/stable/users/explain/colors/colormaps.html).
    """

    def __post_init__(self, cmap_name: str):
        from mizani.palettes import cmap_pal

        super().__post_init__()
        self.palette = cmap_pal(cmap_name)


@dataclass
class scale_fill_cmap(scale_color_cmap):
    """
    Create color scales using Matplotlib colormaps
    """

    _aesthetics = ["fill"]


@dataclass
class scale_color_cmap_d(scale_discrete):
    """
    A discrete color scales using Matplotlib colormaps

    See Also
    --------
    [](`matplotlib.cm`)
    [](`matplotlib.colors`)
    """

    cmap_name: InitVar[str] = "viridis"
    """
    A standard Matplotlib colormap name. The default is `viridis`.
    For the list of names checkout the output of
    `matplotlib.cm.cmap_d.keys()` or see the
    `documentation <http://matplotlib.org/users/colormaps.html>`_.
    """
    _aesthetics = ["color"]

    def __post_init__(self, cmap_name):
        from mizani.palettes import cmap_d_pal

        super().__post_init__()
        self.palette = cmap_d_pal(cmap_name)


@dataclass
class scale_fill_cmap_d(scale_color_cmap_d):
    """
    Create color scales using Matplotlib colormaps
    """

    _aesthetics = ["fill"]


@dataclass
class scale_color_datetime(scale_datetime, scale_color_cmap):  # pyright: ignore[reportIncompatibleVariableOverride]
    """
    Datetime color scale
    """

    _: KW_ONLY
    guide: Literal["legend", "colorbar"] | None = "colorbar"

    def __post_init__(
        self,
        cmap_name: str,
        date_breaks: str | None,
        date_labels: str | None,
        date_minor_breaks: str | None,
    ):
        from mizani.palettes import cmap_pal

        super().__post_init__(date_breaks, date_labels, date_minor_breaks)
        self.palette = cmap_pal(cmap_name)


@dataclass
class scale_fill_datetime(scale_color_datetime):
    """
    Datetime fill scale
    """

    _aesthetics = ["fill"]


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

from __future__ import division
import colorsys
from itertools import cycle

import numpy as np
import matplotlib as mpl
import matplotlib.colors as mcolors
from matplotlib.colors import LinearSegmentedColormap

from six import string_types
from six.moves import range

from . import husl
from .xkcd_rgb import xkcd_rgb


SEABORN_PALETTES = dict(
    deep=["#4C72B0", "#55A868", "#C44E52",
          "#8172B2", "#CCB974", "#64B5CD"],
    muted=["#4878CF", "#6ACC65", "#D65F5F",
           "#B47CC7", "#C4AD66", "#77BEDB"],
    pastel=["#92C6FF", "#97F0AA", "#FF9F9A",
            "#D0BBFF", "#FFFEA3", "#B0E0E6"],
    bright=["#003FFF", "#03ED3A", "#E8000B",
            "#8A2BE2", "#FFC400", "#00D7FF"],
    dark=["#001C7F", "#017517", "#8C0900",
          "#7600A1", "#B8860B", "#006374"],
    colorblind=["#0072B2", "#009E73", "#D55E00",
                "#CC79A7", "#F0E442", "#56B4E9"]
    )

crayons = {'Almond': '#EFDECD',
           'Antique Brass': '#CD9575',
           'Apricot': '#FDD9B5',
           'Aquamarine': '#78DBE2',
           'Asparagus': '#87A96B',
           'Atomic Tangerine': '#FFA474',
           'Banana Mania': '#FAE7B5',
           'Beaver': '#9F8170',
           'Bittersweet': '#FD7C6E',
           'Black': '#000000',
           'Blue': '#1F75FE',
           'Blue Bell': '#A2A2D0',
           'Blue Green': '#0D98BA',
           'Blue Violet': '#7366BD',
           'Blush': '#DE5D83',
           'Brick Red': '#CB4154',
           'Brown': '#B4674D',
           'Burnt Orange': '#FF7F49',
           'Burnt Sienna': '#EA7E5D',
           'Cadet Blue': '#B0B7C6',
           'Canary': '#FFFF99',
           'Caribbean Green': '#00CC99',
           'Carnation Pink': '#FFAACC',
           'Cerise': '#DD4492',
           'Cerulean': '#1DACD6',
           'Chestnut': '#BC5D58',
           'Copper': '#DD9475',
           'Cornflower': '#9ACEEB',
           'Cotton Candy': '#FFBCD9',
           'Dandelion': '#FDDB6D',
           'Denim': '#2B6CC4',
           'Desert Sand': '#EFCDB8',
           'Eggplant': '#6E5160',
           'Electric Lime': '#CEFF1D',
           'Fern': '#71BC78',
           'Forest Green': '#6DAE81',
           'Fuchsia': '#C364C5',
           'Fuzzy Wuzzy': '#CC6666',
           'Gold': '#E7C697',
           'Goldenrod': '#FCD975',
           'Granny Smith Apple': '#A8E4A0',
           'Gray': '#95918C',
           'Green': '#1CAC78',
           'Green Yellow': '#F0E891',
           'Hot Magenta': '#FF1DCE',
           'Inchworm': '#B2EC5D',
           'Indigo': '#5D76CB',
           'Jazzberry Jam': '#CA3767',
           'Jungle Green': '#3BB08F',
           'Laser Lemon': '#FEFE22',
           'Lavender': '#FCB4D5',
           'Macaroni and Cheese': '#FFBD88',
           'Magenta': '#F664AF',
           'Mahogany': '#CD4A4C',
           'Manatee': '#979AAA',
           'Mango Tango': '#FF8243',
           'Maroon': '#C8385A',
           'Mauvelous': '#EF98AA',
           'Melon': '#FDBCB4',
           'Midnight Blue': '#1A4876',
           'Mountain Meadow': '#30BA8F',
           'Navy Blue': '#1974D2',
           'Neon Carrot': '#FFA343',
           'Olive Green': '#BAB86C',
           'Orange': '#FF7538',
           'Orchid': '#E6A8D7',
           'Outer Space': '#414A4C',
           'Outrageous Orange': '#FF6E4A',
           'Pacific Blue': '#1CA9C9',
           'Peach': '#FFCFAB',
           'Periwinkle': '#C5D0E6',
           'Piggy Pink': '#FDDDE6',
           'Pine Green': '#158078',
           'Pink Flamingo': '#FC74FD',
           'Pink Sherbert': '#F78FA7',
           'Plum': '#8E4585',
           'Purple Heart': '#7442C8',
           "Purple Mountains' Majesty": '#9D81BA',
           'Purple Pizzazz': '#FE4EDA',
           'Radical Red': '#FF496C',
           'Raw Sienna': '#D68A59',
           'Razzle Dazzle Rose': '#FF48D0',
           'Razzmatazz': '#E3256B',
           'Red': '#EE204D',
           'Red Orange': '#FF5349',
           'Red Violet': '#C0448F',
           "Robin's Egg Blue": '#1FCECB',
           'Royal Purple': '#7851A9',
           'Salmon': '#FF9BAA',
           'Scarlet': '#FC2847',
           "Screamin' Green": '#76FF7A',
           'Sea Green': '#93DFB8',
           'Sepia': '#A5694F',
           'Shadow': '#8A795D',
           'Shamrock': '#45CEA2',
           'Shocking Pink': '#FB7EFD',
           'Silver': '#CDC5C2',
           'Sky Blue': '#80DAEB',
           'Spring Green': '#ECEABE',
           'Sunglow': '#FFCF48',
           'Sunset Orange': '#FD5E53',
           'Tan': '#FAA76C',
           'Tickle Me Pink': '#FC89AC',
           'Timberwolf': '#DBD7D2',
           'Tropical Rain Forest': '#17806D',
           'Tumbleweed': '#DEAA88',
           'Turquoise Blue': '#77DDE7',
           'Unmellow Yellow': '#FFFF66',
           'Violet (Purple)': '#926EAE',
           'Violet Red': '#F75394',
           'Vivid Tangerine': '#FFA089',
           'Vivid Violet': '#8F509D',
           'White': '#FFFFFF',
           'Wild Blue Yonder': '#A2ADD0',
           'Wild Strawberry': '#FF43A4',
           'Wild Watermelon': '#FC6C85',
           'Wisteria': '#CDA4DE',
           'Yellow': '#FCE883',
           'Yellow Green': '#C5E384',
           'Yellow Orange': '#FFAE42'}


def desaturate(color, prop):
    """Decrease the saturation channel of a color by some percent.

    Parameters
    ----------
    color : matplotlib color
        hex, rgb-tuple, or html color name
    prop : float
        saturation channel of color will be multiplied by this value

    Returns
    -------
    new_color : rgb tuple
        desaturated color code in RGB tuple representation

    """
    # Check inputs
    if not 0 <= prop <= 1:
        raise ValueError("prop must be between 0 and 1")

    # Get rgb tuple rep
    rgb = mcolors.colorConverter.to_rgb(color)

    # Convert to hls
    h, l, s = colorsys.rgb_to_hls(*rgb)

    # Desaturate the saturation channel
    s *= prop

    # Convert back to rgb
    new_color = colorsys.hls_to_rgb(h, l, s)

    return new_color


def set_hls_values(color, h=None, l=None, s=None):
    """Independently manipulate the h, l, or s channels of a color.
    Parameters
    ----------
    color : matplotlib color
        hex, rgb-tuple, or html color name
    h, l, s : floats between 0 and 1, or None
        new values for each channel in hls space
    Returns
    -------
    new_color : rgb tuple
        new color code in RGB tuple representation
    """
    # Get rgb tuple representation
    rgb = mcolors.colorConverter.to_rgb(color)
    vals = list(colorsys.rgb_to_hls(*rgb))
    for i, val in enumerate([h, l, s]):
        if val is not None:
            vals[i] = val

    rgb = colorsys.hls_to_rgb(*vals)
    return rgb


class _ColorPalette(list):
    """Set the color palette in a with statement, otherwise be a list."""
    def __enter__(self):
        """Open the context."""
        from .rcmod import set_palette
        self._orig_palette = color_palette()
        set_palette(self, len(self))
        return self

    def __exit__(self, *args):
        """Close the context."""
        from .rcmod import set_palette
        set_palette(self._orig_palette, len(self._orig_palette))


def color_palette(palette=None, n_colors=None, desat=None):
    """Return a list of colors defining a color palette.

    Availible seaborn palette names:
        deep, muted, bright, pastel, dark, colorblind

    Other options:
        hls, husl, any named matplotlib palette, list of colors

    Calling this function with ``palette=None`` will return the current
    matplotlib color cycle.

    Matplotlib paletes can be specified as reversed palettes by appending
    "_r" to the name or as dark palettes by appending "_d" to the name.
    (These options are mutually exclusive, but the resulting list of colors
    can also be reversed).

    This function can also be used in a ``with`` statement to temporarily
    set the color cycle for a plot or set of plots.

    Parameters
    ----------
    palette: None, string, or sequence, optional
        Name of palette or None to return current palette. If a sequence, input
        colors are used but possibly cycled and desaturated.
    n_colors : int, optional
        Number of colors in the palette. If ``None``, the default will depend
        on how ``palette`` is specified. Named palettes default to 6 colors,
        but grabbing the current palette or passing in a list of colors will
        not change the number of colors unless this is specified. Asking for
        more colors than exist in the palette will cause it to cycle.
    desat : float, optional
        Proportion to desaturate each color by.

    Returns
    -------
    palette : list of RGB tuples.
        Color palette. Behaves like a list, but can be used as a context
        manager and possesses an ``as_hex`` method to convert to hex color
        codes.

    See Also
    --------
    set_palette : Set the default color cycle for all plots.
    set_color_codes : Reassign color codes like ``"b"``, ``"g"``, etc. to
                      colors from one of the seaborn palettes.
    """
    if palette is None:
        palette = mpl.rcParams["axes.color_cycle"]
        if n_colors is None:
            n_colors = len(palette)

    elif not isinstance(palette, string_types):
        palette = palette
        if n_colors is None:
            n_colors = len(palette)
    else:

        if n_colors is None:
            n_colors = 6

        if palette == "hls":
            palette = hls_palette(n_colors)
        elif palette == "husl":
            palette = husl_palette(n_colors)
        elif palette.lower() == "jet":
            raise ValueError("No.")
        elif palette in SEABORN_PALETTES:
            palette = SEABORN_PALETTES[palette]
        elif palette in dir(mpl.cm):
            palette = mpl_palette(palette, n_colors)
        elif palette[:-2] in dir(mpl.cm):
            palette = mpl_palette(palette, n_colors)
        else:
            raise ValueError("%s is not a valid palette name" % palette)

    if desat is not None:
        palette = [desaturate(c, desat) for c in palette]

    # Always return as many colors as we asked for
    pal_cycle = cycle(palette)
    palette = [next(pal_cycle) for _ in range(n_colors)]

    # Always return in r, g, b tuple format
    try:
        palette = map(mpl.colors.colorConverter.to_rgb, palette)
        palette = _ColorPalette(palette)
    except ValueError:
        raise ValueError("Could not generate a palette for %s" % str(palette))

    return palette


def hls_palette(n_colors=6, h=.01, l=.6, s=.65):
    """Get a set of evenly spaced colors in HLS hue space.

    h, l, and s should be between 0 and 1

    Parameters
    ----------

    n_colors : int
        number of colors in the palette
    h : float
        first hue
    l : float
        lightness
    s : float
        saturation

    Returns
    -------
    palette : seaborn color palette
        List-like object of colors as RGB tuples.

    See Also
    --------
    husl_palette : Make a palette using evently spaced circular hues in the
                   HUSL system.

    """
    hues = np.linspace(0, 1, n_colors + 1)[:-1]
    hues += h
    hues %= 1
    hues -= hues.astype(int)
    palette = [colorsys.hls_to_rgb(h_i, l, s) for h_i in hues]
    return _ColorPalette(palette)


def husl_palette(n_colors=6, h=.01, s=.9, l=.65):
    """Get a set of evenly spaced colors in HUSL hue space.

    h, s, and l should be between 0 and 1

    Parameters
    ----------

    n_colors : int
        number of colors in the palette
    h : float
        first hue
    s : float
        saturation
    l : float
        lightness

    Returns
    -------
    palette : seaborn color palette
        List-like object of colors as RGB tuples.
    """
    hues = np.linspace(0, 1, n_colors + 1)[:-1]
    hues += h
    hues %= 1
    hues *= 359
    s *= 99
    l *= 99
    palette = [husl.husl_to_rgb(h_i, s, l) for h_i in hues]
    return _ColorPalette(palette)


def mpl_palette(name, n_colors=6):
    """Return discrete colors from a matplotlib palette.

    Note that this handles the qualitative colorbrewer palettes
    properly, although if you ask for more colors than a particular
    qualitative palette can provide you will get fewer than you are
    expecting. In contrast, asking for qualitative color brewer palettes
    using :func:`color_palette` will return the expected number of colors,
    but they will cycle.

    Parameters
    ----------
    name : string
        Name of the palette. This should be a named matplotlib colormap.
    n_colors : int
        Number of discrete colors in the palette.

    Returns
    -------
    palette or cmap : seaborn color palette or matplotlib colormap
        List-like object of colors as RGB tuples, or colormap object that
        can map continuous values to colors, depending on the value of the
        ``as_cmap`` parameter.

    """
    brewer_qual_pals = {"Accent": 8, "Dark2": 8, "Paired": 12,
                        "Pastel1": 9, "Pastel2": 8,
                        "Set1": 9, "Set2": 8, "Set3": 12}

    if name.endswith("_d"):
        pal = ["#333333"]
        pal.extend(color_palette(name.replace("_d", "_r"), 2))
        cmap = blend_palette(pal, n_colors, as_cmap=True)
    else:
        cmap = getattr(mpl.cm, name)
    if name in brewer_qual_pals:
        bins = np.linspace(0, 1, brewer_qual_pals[name])[:n_colors]
    else:
        bins = np.linspace(0, 1, n_colors + 2)[1:-1]
    palette = list(map(tuple, cmap(bins)[:, :3]))

    return _ColorPalette(palette)


def _color_to_rgb(color, input):
    """Add some more flexibility to color choices."""
    if input == "hls":
        color = colorsys.hls_to_rgb(*color)
    elif input == "husl":
        color = husl.husl_to_rgb(*color)
    elif input == "xkcd":
        color = xkcd_rgb[color]
    return color


def dark_palette(color, n_colors=6, reverse=False, as_cmap=False,
                 input="rgb"):
    """Make a sequential palette that blends from dark to ``color``.

    This kind of palette is good for data that range between relatively
    uninteresting low values and interesting high values.

    The ``color`` parameter can be specified in a number of ways, including
    all options for defining a color in matplotlib and several additional
    color spaces that are handled by seaborn. You can also use the database
    of named colors from the XKCD color survey.

    Parameters
    ----------
    color : base color for high values
        hex, rgb-tuple, or html color name
    n_colors : int, optional
        number of colors in the palette
    reverse : bool, optional
        if True, reverse the direction of the blend
    as_cmap : bool, optional
        if True, return as a matplotlib colormap instead of list
    input : {'rgb', 'hls', 'husl', xkcd'}
        Color space to interpret the input color. The first three options
        apply to tuple inputs and the latter applies to string inputs.

    Returns
    -------
    palette or cmap : seaborn color palette or matplotlib colormap
        List-like object of colors as RGB tuples, or colormap object that
        can map continuous values to colors, depending on the value of the
        ``as_cmap`` parameter.

    See Also
    --------
    light_palette : Create a sequential palette with bright low values.
    diverging_palette : Create a diverging palette with two colors.
    """
    color = _color_to_rgb(color, input)
    gray = "#222222"
    colors = [color, gray] if reverse else [gray, color]
    return blend_palette(colors, n_colors, as_cmap)


def light_palette(color, n_colors=6, reverse=False, as_cmap=False,
                  input="rgb"):
    """Make a sequential palette that blends from light to ``color``.

    This kind of palette is good for data that range between relatively
    uninteresting low values and interesting high values.

    The ``color`` parameter can be specified in a number of ways, including
    all options for defining a color in matplotlib and several additional
    color spaces that are handled by seaborn. You can also use the database
    of named colors from the XKCD color survey.

    Parameters
    ----------
    color : base color for high values
        hex code, html color name, or tuple in ``input`` space.
    n_colors : int, optional
        number of colors in the palette
    reverse : bool, optional
        if True, reverse the direction of the blend
    as_cmap : bool, optional
        if True, return as a matplotlib colormap instead of list
    input : {'rgb', 'hls', 'husl', xkcd'}
        Color space to interpret the input color. The first three options
        apply to tuple inputs and the latter applies to string inputs.

    Returns
    -------
    palette or cmap : seaborn color palette or matplotlib colormap
        List-like object of colors as RGB tuples, or colormap object that
        can map continuous values to colors, depending on the value of the
        ``as_cmap`` parameter.

    See Also
    --------
    dark_palette : Create a sequential palette with dark low values.
    diverging_palette : Create a diverging palette with two colors.

    """
    color = _color_to_rgb(color, input)
    light = set_hls_values(color, l=.95)
    colors = [color, light] if reverse else [light, color]
    return blend_palette(colors, n_colors, as_cmap)


def _flat_palette(color, n_colors=6, reverse=False, as_cmap=False,
                  input="rgb"):
    """Make a sequential palette that blends from gray to ``color``.

    Parameters
    ----------
    color : matplotlib color
        hex, rgb-tuple, or html color name
    n_colors : int, optional
        number of colors in the palette
    reverse : bool, optional
        if True, reverse the direction of the blend
    as_cmap : bool, optional
        if True, return as a matplotlib colormap instead of list

    Returns
    -------
    palette : list or colormap
    dark_palette : Create a sequential palette with dark low values.

    """
    color = _color_to_rgb(color, input)
    flat = desaturate(color, 0)
    colors = [color, flat] if reverse else [flat, color]
    return blend_palette(colors, n_colors, as_cmap)


def diverging_palette(h_neg, h_pos, s=75, l=50, sep=10, n=6, center="light",
                      as_cmap=False):
    """Make a diverging palette between two HUSL colors.

    If you are using the IPython notebook, you can also choose this palette
    interactively with the :func:`choose_diverging_palette` function.

    Parameters
    ----------
    h_neg, h_pos : float in [0, 359]
        Anchor hues for negative and positive extents of the map.
    s : float in [0, 100], optional
        Anchor saturation for both extents of the map.
    l : float in [0, 100], optional
        Anchor lightness for both extents of the map.
    n : int, optional
        Number of colors in the palette (if not returning a cmap)
    center : {"light", "dark"}, optional
        Whether the center of the palette is light or dark
    as_cmap : bool, optional
        If true, return a matplotlib colormap object rather than a
        list of colors.

    Returns
    -------
    palette or cmap : seaborn color palette or matplotlib colormap
        List-like object of colors as RGB tuples, or colormap object that
        can map continuous values to colors, depending on the value of the
        ``as_cmap`` parameter.

    See Also
    --------
    dark_palette : Create a sequential palette with dark values.
    light_palette : Create a sequential palette with light values.

    """
    palfunc = dark_palette if center == "dark" else light_palette
    neg = palfunc((h_neg, s, l), 128 - (sep / 2), reverse=True, input="husl")
    pos = palfunc((h_pos, s, l), 128 - (sep / 2), input="husl")
    midpoint = dict(light=[(.95, .95, .95, 1.)],
                    dark=[(.133, .133, .133, 1.)])[center]
    mid = midpoint * sep
    pal = blend_palette(np.concatenate([neg, mid,  pos]), n, as_cmap=as_cmap)
    return pal


def blend_palette(colors, n_colors=6, as_cmap=False):
    """Make a palette that blends between a list of colors.

    Parameters
    ----------
    colors : sequence of matplotlib colors
        hex, rgb-tuple, or html color name
    n_colors : int, optional
        number of colors in the palette
    as_cmap : bool, optional
        if True, return as a matplotlib colormap instead of list

    Returns
    -------
    palette : list or colormap

    """
    name = "-".join(map(str, colors))
    pal = mpl.colors.LinearSegmentedColormap.from_list(name, colors)
    if not as_cmap:
        pal = pal(np.linspace(0, 1, n_colors))
    return pal


def xkcd_palette(colors):
    """Make a palette with color names from the xkcd color survey.

    See xkcd for the full list of colors: http://xkcd.com/color/rgb/

    This is just a simple wrapper around the ``seaborn.xkcd_rgb`` dictionary.

    Parameters
    ----------
    colors : list of strings
        List of keys in the ``seaborn.xkcd_rgb`` dictionary.

    Returns
    -------
    palette : seaborn color palette
        Returns the list of colors as RGB tuples in an object that behaves like
        other seaborn color palettes.

    See Also
    --------
    crayon_palette : Make a palette with Crayola crayon colors.

    """
    palette = [xkcd_rgb[name] for name in colors]
    return color_palette(palette, len(palette))


def crayon_palette(colors):
    """Make a palette with color names from Crayola crayons.

    Colors are taken from here:
    http://en.wikipedia.org/wiki/List_of_Crayola_crayon_colors

    This is just a simple wrapper around the ``seaborn.crayons`` dictionary.

    Parameters
    ----------
    colors : list of strings
        List of keys in the ``seaborn.crayons`` dictionary.

    Returns
    -------
    palette : seaborn color palette
        Returns the list of colors as rgb tuples in an object that behaves like
        other seaborn color palettes.

    See Also
    --------
    xkcd_palette : Make a palette with named colors from the XKCD color survey.

    """
    palette = [crayons[name] for name in colors]
    return color_palette(palette, len(palette))


def cubehelix_palette(n_colors=6, start=0, rot=.4, gamma=1.0, hue=0.8,
                      light=.85, dark=.15, reverse=False, as_cmap=False):
    """Make a sequential palette from the cubehelix system.

    This produces a colormap with linearly-decreasing (or increasing)
    brightness. That means that information will be preserved if printed to
    black and white or viewed by someone who is colorblind.  "cubehelix" is
    also availible as a matplotlib-based palette, but this function gives the
    user more control over the look of the palette and has a different set of
    defaults.

    Parameters
    ----------
    n_colors : int
        Number of colors in the palette.
    start : float, 0 <= start <= 3
        The hue at the start of the helix.
    rot : float
        Rotations around the hue wheel over the range of the palette.
    gamma : float 0 <= gamma
        Gamma factor to emphasize darker (gamma < 1) or lighter (gamma > 1)
        colors.
    hue : float, 0 <= hue <= 1
        Saturation of the colors.
    dark : float 0 <= dark <= 1
        Intensity of the darkest color in the palette.
    light : float 0 <= light <= 1
        Intensity of the lightest color in the palette.
    reverse : bool
        If True, the palette will go from dark to light.
    as_cmap : bool
        If True, return a matplotlib colormap instead of a list of colors.

    Returns
    -------
    palette or cmap : seaborn color palette or matplotlib colormap
        List-like object of colors as RGB tuples, or colormap object that
        can map continuous values to colors, depending on the value of the
        ``as_cmap`` parameter.

    See Also
    --------
    choose_cubehelix_palette : Launch an interactive widget to select cubehelix
                               palette parameters.
    dark_palette : Create a sequential palette with dark low values.
    light_palette : Create a sequential palette with bright low values.

    References
    ----------
    Green, D. A. (2011). "A colour scheme for the display of astronomical
    intensity images". Bulletin of the Astromical Society of India, Vol. 39,
    p. 289-295.
    """
    cdict = mpl._cm.cubehelix(gamma, start, rot, hue)
    cmap = mpl.colors.LinearSegmentedColormap("cubehelix", cdict)

    x = np.linspace(light, dark, n_colors)
    pal = cmap(x)[:, :3].tolist()
    if reverse:
        pal = pal[::-1]

    if as_cmap:
        x_256 = np.linspace(light, dark, 256)
        if reverse:
            x_256 = x_256[::-1]
        pal_256 = cmap(x_256)
        cmap = mpl.colors.ListedColormap(pal_256)
        return cmap
    else:
        return _ColorPalette(pal)


def set_color_codes(palette="deep"):
    """Change how matplotlib color shorthands are interpreted.

    Calling this will change how shorthand codes like "b" or "g"
    are interpreted by matplotlib in subsequent plots.

    Parameters
    ----------
    palette : {deep, muted, pastel, dark, bright, colorblind}
        Named seaborn palette to use as the source of colors.

    See Also
    --------
    set : Color codes can be set through the high-level seaborn style
          manager.
    set_palette : Color codes can also be set through the function that
                  sets the matplotlib color cycle.
    """
    if palette == "reset":
        colors = [(0., 0., 1.), (0., .5, 0.), (1., 0., 0.), (.75, .75, 0.),
                  (.75, .75, 0.), (0., .75, .75), (0., 0., 0.)]
    else:
        colors = SEABORN_PALETTES[palette] + [(.1, .1, .1)]
    for code, color in zip("bgrmyck", colors):
        rgb = mpl.colors.colorConverter.to_rgb(color)
        mpl.colors.colorConverter.colors[code] = rgb
        mpl.colors.colorConverter.cache[code] = rgb


def _init_mutable_colormap():
    """Create a matplotlib colormap that will be updated by the widgets."""
    greys = color_palette("Greys", 256)
    cmap = LinearSegmentedColormap.from_list("interactive", greys)
    cmap._init()
    cmap._set_extremes()
    return cmap


def _update_lut(cmap, colors):
    """Change the LUT values in a matplotlib colormap in-place."""
    cmap._lut[:256] = colors
    cmap._set_extremes()

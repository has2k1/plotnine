import numpy as np
from matplotlib.colors import rgb2hex
from ..utils.color import ColorHCL
from copy import deepcopy
import six


def hue_pal(h=(0 + 15, 360 + 15), c=100, l=65, h_start=0, direction=1):
    """
    Utility for making hue palettes for color schemes.
    """
    c /= 100.
    l /= 100.
    hcl = ColorHCL()
    def func(n):
        y = deepcopy(h)
        if (y[1] - y[0]) % 360 < 1:
            y = (y[0], y[1] - 360. / n)
        hues = []
        for x in np.linspace(y[0], y[1], n):
            hue = ((x + h_start) % 360) * direction
            hues.append(rgb2hex(hcl(hue, c, l)))
        return hues
    return func


def color_gen(n_colors, colors=None):
    """
    Generator that will infinitely produce colors when asked politely. Colors
    are based on the color wheel and the default colors will be chosen by
    maximizing the distance between each color (based on the color wheel).

    Parameters
    ----------
    n_colors: int
        number of colors you need
    colors: list
        a list of colors. can be hex or actual names
    """
    while True:
        if colors is None:
            for color in hue_pal()(n_colors):
                yield color
        else:
            for color in colors:
                yield color


def assign_colors(data, aes, gg):
    """
    Assigns colors to the given data based on the aes and adds the right legend

    We need to take a value an convert it into colors that we can actually
    plot. This means checking to see if we're colorizing a discrete or
    continuous value, checking if their is a colormap, etc.

    Parameters
    ----------
    data : DataFrame
        dataframe which should have shapes assigned to
    aes : aesthetic
        mapping, including a mapping from color to variable
    gg : ggplot object, which holds information and gets a legend assigned

    Returns
    -------
    data : DataFrame
        the changed dataframe
    """
    if 'color' in aes:
        color_col = aes['color']
        numeric_cols = set(data._get_numeric_data().columns)
        bool_cols = set(data._get_bool_data().columns)
        continuous_cols = numeric_cols - bool_cols
        if color_col in continuous_cols:
            data = assign_continuous_colors(data, gg, color_col)
        else:
            data = assign_discrete_colors(data, gg, color_col)

    return data


def assign_continuous_colors(data, gg, color_col):
    """
    Logic to assign colors in the continuous case.

    Handle continuous colors here. We're going to use whatever colormap
    is defined to evaluate for each value. We're then going to convert
    each color to HEX so that it can fit in 1 column. This will make it
    much easier when creating layers. We're also going to evaluate the
    quantiles for that particular column to generate legend scales. This
    isn't what ggplot does, but it's good enough for now.

    Parameters
    ----------
    data : DataFrame
        dataframe which should have shapes assigned to
    gg : ggplot object, which holds information and gets a legend assigned
    color_col : The column we are using to color.

    Returns
    -------
    data : DataFrame
        the changed dataframe
    """
    values = data[color_col].tolist()
    values = [(i - min(values)) / (max(values) - min(values)) for i in values]
    color_mapping = gg.colormap(values)[::, :3]
    data["color_mapping"] = [rgb2hex(value) for value in color_mapping]
    quantiles = np.percentile(gg.data[color_col], [0, 25, 50, 75, 100])
    key_colors = gg.colormap([0, 25, 50, 75, 100])[::, :3]
    key_colors = [rgb2hex(value) for value in key_colors]
    gg.add_to_legend("color", dict(zip(key_colors, quantiles)),
                     scale_type="continuous")
    return data


def assign_discrete_colors(data, gg, color_col):
    """
    Logic to assign colors in the discrete case.

    We're going to check and see if the user has defined their own color
    palette. If they have then we'll use those colors for mapping. If not,
    then we'll generate some default colors. We also have to be careful here
    because for some odd reason the next() function is different in Python 2.7
    and Python 3.0. Once we've done that we generate the legends based off
    the (color -> value) mapping.

    Parameters
    ----------
    data : DataFrame
        dataframe which should have shapes assigned to
    gg : ggplot object, which holds information and gets a legend assigned
    color_col : The column we are using to color.

    Returns
    -------
    data : DataFrame
        the changed dataframe
    """
    possible_colors = np.unique(data[color_col])
    if gg.manual_color_list:
        color = color_gen(len(possible_colors), gg.manual_color_list)
    else:
        color = color_gen(len(possible_colors))
    color_mapping = dict((value, six.next(color)) for value in possible_colors)
    data["color_mapping"] = data[color_col].apply(lambda x: color_mapping[x])
    gg.add_to_legend("color", dict((v, k) for k, v in color_mapping.items()))
    return data

import sys
import numpy as np
from matplotlib.colors import rgb2hex

COLORS = [
    "#000000",
    "#E69F00",
    "#56B4E9",
    "#009E73",
    "#F0E442",
    "#0072B2",
    "#D55E00",
    "#CC79A7"
]

def color_gen(colors=COLORS):
    """
    Generator that will infinitely produce colors when asked politely
    TODO: This needs to be updated with better colors, but it will do for now.

    params:
        colors - a list of colors. can be hex or actual names
    """
    while True:
        for color in colors:
            yield color


def assign_colors(gg):
    """
    We need to take a value an convert it into colors that we can actually
    plot. This means checking to see if we're colorizing a discrete or 
    continuous value, checking if their is a colormap, etc.

    params:
        gg - a ggplot instance
    """
    if 'color' in gg.aesthetics:
        color_col = gg.aesthetics['color']
        # Handle continuous colors here. We're going to use whatever colormap
        # is defined to evaluate for each value. We're then going to convert
        # each color to HEX so that it can fit in 1 column. This will make it
        # much easier when creating layers. We're also going to evaluate the 
        # quantiles for that particular column to generate legend scales. This
        # isn't what ggplot does, but it's good enough for now.
        if color_col in gg.data._get_numeric_data().columns:
            values = gg.data[color_col].tolist()
            # Normalize the values for the colormap
            values = [(i - min(values)) / (max(values) - min(values)) for i in values]
            color_mapping = gg.colormap(values)[::,:3]
            gg.data["color_mapping"] = [rgb2hex(value) for value in color_mapping]
            quantiles = np.percentile(gg.data[color_col], [0, 25, 50, 75, 100])
            key_colors = gg.colormap([0, 25, 50, 75, 100])[::,:3]
            key_colors = [rgb2hex(value) for value in key_colors]
            gg.legend["color"] = dict(zip(key_colors, quantiles))

        # Handle discrete colors here. We're goign to check and see if the user
        # has defined their own color palatte. If they have then we'll use those
        # colors for mapping. If not, then we'll generate some default colors.
        # We also have to be careful here becasue for some odd reason the next()
        # function is different in Python 2.7 and Python 3.0. Once we've done that
        # we generate the legends based off the the (color -> value) mapping.
        else:
            if gg.manual_color_list:
                color = color_gen(gg.manual_color_list)
            else:
                color = color_gen()
            possible_colors = np.unique(gg.data[color_col])
            if sys.hexversion > 0x03000000:
                color_mapping = {value: color.__next__() for value in possible_colors}
            else:
                color_mapping = {value: color.next() for value in possible_colors}
            gg.data["color_mapping"] = gg.data[color_col].apply(lambda x: color_mapping[x])
            gg.legend["color"] = { v: k for k, v in color_mapping.items() }

    return gg


if __name__ == '__main__':
    import pandas as pd
    from aes import aes
    from ggplot import ggplot

    df = pd.DataFrame({
        "x": ["a", "b", "c"] + ["a", "b", "c"],
        "y": [1, 2, 3] + [1, 2, 3],
        "z": [4, 5, 6] + [4, 5, 6]
    })

    gg = ggplot(df, aes(x="x", y="y", color="y"))
    gg.manual_color_list = None
    gg = assign_colors(gg)
    print gg.data
    print gg.legend

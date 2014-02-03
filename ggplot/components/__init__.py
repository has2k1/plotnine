from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from .aes import aes
from . import colors, shapes, size, linestyles


def assign_visual_mapping(data, aes, gg):
    """Assigns the visual mapping to the given data and adds the right legend

    Parameters
    ----------
    data : DataFrame
        dataframe which should have shapes assigned to
    aes : aesthetic
        mapping, visual value to variable
    gg : ggplot object, which holds information and gets a legend assigned

    Returns
    -------
    data : DataFrame
        the changed dataframe with visual values added
    """
    data = colors.assign_colors(data, aes, gg)
    data = size.assign_sizes(data, aes, gg)
    data = linestyles.assign_linestyles(data, aes, gg)
    data = shapes.assign_shapes(data, aes, gg)
    return data

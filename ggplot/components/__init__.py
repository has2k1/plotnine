from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from .aes import aes
from . import colors, shapes, size, linetypes, alphas


def assign_visual_mapping(data, aes, gg):
    """Assigns the visual mapping to the given data and adds the right legend

    Parameters
    ----------
    data : DataFrame
        dataframe which should have aesthetic mappings assigned to
    aes : aesthetic
        mapping, visual value to variable
    gg : ggplot object,
        It holds global configuration values needed by
        some of the mapping functions

    Returns
    -------
    data : DataFrame
        the changed dataframe with visual values added
    legend : dict
        A legend as specified in `components.legend`
    """
    legend = {}
    data, legend['color'] = colors.assign_colors(data, aes, gg, 'color')
    data, legend['fill'] = colors.assign_colors(data, aes, gg, 'fill')
    data, legend['size'] = size.assign_sizes(data, aes)
    data, legend['linetype'] = linetypes.assign_linetypes(data, aes)
    data, legend['shape'] = shapes.assign_shapes(data, aes)
    data, legend['alpha'] = alphas.assign_alphas(data, aes)

    # Delete empty entries in the legend
    for _aes_name in ('color', 'fill', 'size', 'linetype', 'shape', 'alpha'):
        if not legend[_aes_name]:
            del legend[_aes_name]

    return data, legend

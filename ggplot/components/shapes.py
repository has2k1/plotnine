from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import numpy as np
import sys
import ggplot.utils.six as six


SHAPES = [
    'o',#circle
    '^',#triangle up
    'D',#diamond
    'v',#triangle down
    '+',#plus
    'x',#x
    's',#square
    '*',#star
    'p',#pentagon
    '*'#octagon
]

def shape_gen():
    while True:
        for shape in SHAPES:
            yield shape


def assign_shapes(data, aes, gg):
    """Assigns shapes to the given data based on the aes and adds the right legend

    Parameters
    ----------
    data : DataFrame
        dataframe which should have shapes assigned to
    aes : aesthetic
        mapping, including a mapping from shapes to variable
    gg : ggplot
        object, which holds information and gets a legend assigned

    Returns
    -------
    data : DataFrame
        the changed dataframe
    """
    if 'shape' in aes:
        shape_col = aes['shape']
        possible_shapes = np.unique(data[shape_col])
        shape = shape_gen()
        shape_mapping = {value: six.next(shape) for value in possible_shapes}
        data['shape_mapping'] = data[shape_col].apply(lambda x: shape_mapping[x])
        gg.add_to_legend("marker", {v: k for k, v in shape_mapping.items()})
    return data

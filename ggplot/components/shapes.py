from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import numpy as np
import six


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


def assign_shapes(data, aes):
    """Assigns shapes to the given data based on the aes and adds the right legend

    Parameters
    ----------
    data : DataFrame
        dataframe which should have shapes assigned to
    aes : aesthetic
        mapping, including a mapping from shapes to variable

    Returns
    -------
    data : DataFrame
        the changed dataframe
    legend_entry : dict
        An entry into the legend dictionary.
        Documented in `components.legend`
    """
    legend_entry = dict()
    if 'shape' in aes:
        shape_col = aes['shape']
        possible_shapes = np.unique(data[shape_col])
        shape = shape_gen()
        # marker in matplotlib are not unicode ready in 1.3.1 :-( -> use explicit str()...
        shape_mapping = dict((value, str(six.next(shape))) for value in possible_shapes)
        data[':::shape_mapping:::'] = data[shape_col].apply(
            lambda x: shape_mapping[x])

        legend_entry = {'column_name': shape_col,
                  'dict': dict((v, k) for k, v in shape_mapping.items()),
                  'scale_type': "discrete"}
    return data, legend_entry

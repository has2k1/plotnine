import numpy as np
import sys


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


def assign_shapes(gg):
    if 'shape' in gg.aesthetics:
        shape_col = gg.aesthetics['shape']
        possible_shapes = np.unique(gg.data[shape_col])
        shape = shape_gen()
        if sys.hexversion > 0x03000000:
            shape_mapping = {value: shape.__next__() for value in possible_shapes}
        else:
            shape_mapping = {value: shape.next() for value in possible_shapes}
        #mapping['marker'] = mapping['shape'].replace(shape_mapping)
        gg.data['shape_mapping'] = gg.data[shape_col].apply(lambda x: shape_mapping[x])
        gg.legend["marker"] = { v: k for k, v in shape_mapping.items() }
    return gg

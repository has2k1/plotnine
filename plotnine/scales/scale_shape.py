from warnings import warn

from mizani.palettes import manual_pal

from ..doctools import document
from ..exceptions import PlotnineError, PlotnineWarning
from ..utils import alias
from .scale import scale_discrete, scale_continuous

# All these shapes are filled
shapes = (
    'o',  # circle
    '^',  # triangle up
    's',  # square
    'D',  # Diamond
    'v',  # triangle down
    '*',  # star
    'p',  # pentagon
    '8',  # octagon
    '<',  # triangle left
    'h',  # hexagon1
    '>',  # triangle right
    'H',  # hexagon1
    'd',  # thin diamond
)

unfilled_shapes = (
    '+',  # plus
    'x',  # x
    '.',  # point
    '1',  # tri_down
    '2',  # tri_up
    '3',  # tri_left
    '4',  # tri_right
    ',',  # pixel
    '_',  # hline
    '|',  # vline
    1,    # tickleft
    2,    # tickright
    3,    # tickup
    4,    # tickdown
)


@document
class scale_shape(scale_discrete):
    """
    Scale for shapes

    Parameters
    ----------
    unfilled : bool
        If ``True``, then all shapes will have no interiors
        that can be a filled.
    {superclass_parameters}
    """
    _aesthetics = ['shape']

    def __init__(self, unfilled=False, **kwargs):
        if unfilled:
            self.palette = manual_pal(unfilled_shapes)
        else:
            self.palette = manual_pal(shapes)
        scale_discrete.__init__(self, **kwargs)


@document
class scale_shape_ordinal(scale_shape):
    """
    Scale for shapes

    Parameters
    ----------
    {superclass_parameters}
    """
    _aesthetics = ['shape']

    def __init__(self, **kwargs):
        warn(
            "Using shapes for an ordinal variable is not advised.",
            PlotnineWarning
        )
        super().__init__(**kwargs)


class scale_shape_continuous(scale_continuous):
    def __init__(self):
        raise PlotnineError(
            "A continuous variable can not be mapped to shape")


alias('scale_shape_discrete', scale_shape)

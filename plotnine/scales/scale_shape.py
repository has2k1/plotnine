from warnings import warn

from .._utils.registry import alias
from ..doctools import document
from ..exceptions import PlotnineError, PlotnineWarning
from .scale_continuous import scale_continuous
from .scale_discrete import scale_discrete

# All these shapes are filled
shapes = (
    "o",  # circle
    "^",  # triangle up
    "s",  # square
    "D",  # Diamond
    "v",  # triangle down
    "*",  # star
    "p",  # pentagon
    "8",  # octagon
    "<",  # triangle left
    "h",  # hexagon1
    ">",  # triangle right
    "H",  # hexagon1
    "d",  # thin diamond
)

unfilled_shapes = (
    "+",  # plus
    "x",  # x
    ".",  # point
    "1",  # tri_down
    "2",  # tri_up
    "3",  # tri_left
    "4",  # tri_right
    ",",  # pixel
    "_",  # hline
    "|",  # vline
    0,  # tickleft
    1,  # tickright
    2,  # tickup
    3,  # tickdown
    4,  # caretleft
    5,  # caretright
    6,  # caretup
    7,  # caretdown
)

# For quick lookup
FILLED_SHAPES = set(shapes)
UNFILLED_SHAPES = set(unfilled_shapes)


@document
class scale_shape(scale_discrete):
    """
    Scale for shapes

    Parameters
    ----------
    unfilled :
        If `True`, then all shapes will have no interiors
        that can be a filled.
    {superclass_parameters}
    """

    _aesthetics = ["shape"]

    def __init__(self, unfilled: bool = False, **kwargs):
        from mizani.palettes import manual_pal

        _shapes = unfilled_shapes if unfilled else shapes
        self._palette = manual_pal(_shapes)
        scale_discrete.__init__(self, **kwargs)


@document
class scale_shape_ordinal(scale_shape):
    """
    Scale for shapes

    Parameters
    ----------
    {superclass_parameters}
    """

    _aesthetics = ["shape"]

    def __init__(self, **kwargs):
        warn(
            "Using shapes for an ordinal variable is not advised.",
            PlotnineWarning,
        )
        super().__init__(**kwargs)


class scale_shape_continuous(scale_continuous):
    """
    Continuous scale for shapes

    This is not a valid type of scale.
    """

    def __init__(self):
        raise PlotnineError("A continuous variable can not be mapped to shape")


@alias
class scale_shape_discrete(scale_shape):
    pass

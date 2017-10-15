from __future__ import absolute_import, division, print_function

from mizani.palettes import manual_pal

from ..doctools import document
from ..exceptions import PlotnineError
from ..utils import alias
from .scale import scale_discrete, scale_continuous


linetypes = ['solid', 'dashed', 'dashdot', 'dotted']


@document
class scale_linetype(scale_discrete):
    """
    Scale for line patterns

    Parameters
    ----------
    {superclass_parameters}
    """
    aesthetics = ['linetype']
    palette = staticmethod(manual_pal(linetypes))


class scale_linetype_continuous(scale_continuous):
    def __init__(self):
        raise PlotnineError(
            "A continuous variable can not be mapped to linetype")


alias('scale_linetype_discrete', scale_linetype)

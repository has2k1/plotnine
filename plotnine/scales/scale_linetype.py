from warnings import warn

from mizani.palettes import manual_pal

from ..doctools import document
from ..exceptions import PlotnineError, PlotnineWarning
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

    Notes
    -----
    The available linetypes are
    ``'solid', 'dashed', 'dashdot', 'dotted'``
    If you need more custom linetypes, use
    :class:`~plotnine.scales.scale_linetype_manual`
    """
    _aesthetics = ['linetype']
    palette = staticmethod(manual_pal(linetypes))


@document
class scale_linetype_ordinal(scale_linetype):
    """
    Scale for line patterns

    Parameters
    ----------
    {superclass_parameters}
    """
    _aesthetics = ['linetype']

    def __init__(self, **kwargs):
        warn(
            "Using linetype for an ordinal variable is not advised.",
            PlotnineWarning
        )
        super().__init__(**kwargs)


class scale_linetype_continuous(scale_continuous):
    def __init__(self):
        raise PlotnineError(
            "A continuous variable can not be mapped to linetype")


alias('scale_linetype_discrete', scale_linetype)

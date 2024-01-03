from ..doctools import document
from .geom_path import geom_path

_params = geom_path.DEFAULT_PARAMS.copy()
_params["stat"] = "bin"


@document
class geom_freqpoly(geom_path):
    """
    Frequency polygon

    {usage}

    See [](`~plotnine.geoms.geom_path`) for documentation
    of the parameters.
    """

    DEFAULT_PARAMS = _params

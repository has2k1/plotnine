from __future__ import annotations

import typing

from ..doctools import document
from ..exceptions import PlotnineError
from ..positions import position_jitter
from .geom_point import geom_point

if typing.TYPE_CHECKING:
    from typing import Any

    from plotnine import aes
    from plotnine.typing import DataLike


@document
class geom_jitter(geom_point):
    """
    Scatter plot with points jittered to reduce overplotting

    {usage}

    Parameters
    ----------
    {common_parameters}
    width : float, default=None
        Proportion to jitter in horizontal direction.
        The default value is that from
        [](`~plotnine.positions.position_jitter`)
    height : float, default=None
        Proportion to jitter in vertical direction.
        The default value is that from
        [](`~plotnine.positions.position_jitter`).
    random_state : int | ~numpy.random.RandomState, default=None
        Seed or Random number generator to use. If `None`, then
        numpy global generator [](`numpy.random`) is used.

    See Also
    --------
    plotnine.position_jitter
    plotnine.geom_point
    """

    DEFAULT_PARAMS = {
        "stat": "identity",
        "position": "jitter",
        "na_rm": False,
        "width": None,
        "height": None,
        "random_state": None,
    }

    def __init__(
        self,
        mapping: aes | None = None,
        data: DataLike | None = None,
        **kwargs: Any,
    ):
        if {"width", "height", "random_state"} & set(kwargs):
            if "position" in kwargs:
                raise PlotnineError(
                    "Specify either 'position' or "
                    "'width'/'height'/'random_state'"
                )

            try:
                width = kwargs.pop("width")
            except KeyError:
                width = None

            try:
                height = kwargs.pop("height")
            except KeyError:
                height = None

            try:
                random_state = kwargs.pop("random_state")
            except KeyError:
                random_state = None

            kwargs["position"] = position_jitter(
                width=width, height=height, random_state=random_state
            )
        geom_point.__init__(self, mapping, data, **kwargs)

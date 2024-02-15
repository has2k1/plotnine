from __future__ import annotations

import typing

from .._utils.registry import alias
from ..doctools import document
from .scale_continuous import scale_continuous
from .scale_discrete import scale_discrete

if typing.TYPE_CHECKING:
    from typing import Any, Sequence


class MapTrainMixin:
    """
    Override map and train methods
    """

    guide = None

    def map(self, x, limits=None) -> Sequence[Any]:
        """
        Identity map

        Notes
        -----
        Identity scales bypass the palette completely since the
        map is the identity function.
        """
        return x

    def train(self, x, drop=False):
        # do nothing if no guide,
        # otherwise train so we know what breaks to use
        if self.guide is None:
            return

        return super().train(x)  # pyright: ignore


@document
class scale_color_identity(MapTrainMixin, scale_discrete):
    """
    No color scaling

    Parameters
    ----------
    {superclass_parameters}
    guide : Optional[Literal["legend"]], default=None
        Whether to include a legend.
    """

    _aesthetics = ["color"]


@document
class scale_fill_identity(scale_color_identity):
    """
    No color scaling

    Parameters
    ----------
    {superclass_parameters}
    """

    _aesthetics = ["fill"]


@document
class scale_shape_identity(MapTrainMixin, scale_discrete):
    """
    No shape scaling

    Parameters
    ----------
    {superclass_parameters}
    guide : Optional[Literal["legend"]], default=None
        Whether to include a legend.
    """

    _aesthetics = ["shape"]


@document
class scale_linetype_identity(MapTrainMixin, scale_discrete):
    """
    No linetype scaling

    Parameters
    ----------
    {superclass_parameters}
    guide : Optional[Literal["legend"]], default=None
        Whether to include a legend.
    """

    _aesthetics = ["linetype"]


@document
class scale_alpha_identity(MapTrainMixin, scale_continuous):
    """
    No alpha scaling

    Parameters
    ----------
    {superclass_parameters}
    guide : Optional[Literal["legend"]], default=None
        Whether to include a legend.
    """

    _aesthetics = ["alpha"]


@document
class scale_size_identity(MapTrainMixin, scale_continuous):
    """
    No size scaling

    Parameters
    ----------
    {superclass_parameters}
    guide : Optional[Literal["legend"]], default=None
        Whether to include a legend.
    """

    _aesthetics = ["size"]


# American to British spelling
@alias
class scale_colour_identity(scale_color_identity):
    pass

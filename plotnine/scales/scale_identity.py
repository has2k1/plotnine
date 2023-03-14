from __future__ import annotations

import typing

from ..doctools import document
from ..utils import alias, identity
from .scale import scale_continuous, scale_discrete

if typing.TYPE_CHECKING:
    from typing import Literal


class MapTrainMixin:
    """
    Override map and train methods
    """

    guide: Literal["legend"] | None = None

    def map(self, x):
        return x

    def train(self, x):
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
    guide : None | 'legend'
        Whether to include a legend. Default is None.
    """

    _aesthetics = ["color"]
    palette = staticmethod(identity)


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
    guide : None | 'legend'
        Whether to include a legend. Default is None.
    """

    _aesthetics = ["shape"]
    palette = staticmethod(identity)


@document
class scale_linetype_identity(MapTrainMixin, scale_discrete):
    """
    No linetype scaling

    Parameters
    ----------
    {superclass_parameters}
    guide : None | 'legend'
        Whether to include a legend. Default is None.
    """

    _aesthetics = ["linetype"]
    palette = staticmethod(identity)


@document
class scale_alpha_identity(MapTrainMixin, scale_continuous):
    """
    No alpha scaling

    Parameters
    ----------
    {superclass_parameters}
    guide : None | 'legend'
        Whether to include a legend. Default is None.
    """

    _aesthetics = ["alpha"]
    palette = staticmethod(identity)


@document
class scale_size_identity(MapTrainMixin, scale_continuous):
    """
    No size scaling

    Parameters
    ----------
    {superclass_parameters}
    guide : None | 'legend'
        Whether to include a legend. Default is None.
    """

    _aesthetics = ["size"]
    palette = staticmethod(identity)


# American to British spelling
alias("scale_colour_identity", scale_color_identity)

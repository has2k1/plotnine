from __future__ import annotations

import typing

from ..doctools import document
from ..utils import alias
from .scale import scale_continuous, scale_discrete

if typing.TYPE_CHECKING:
    from typing import Any, Literal, Sequence


class MapTrainMixin:
    """
    Override map and train methods
    """

    guide: Literal["legend"] | None = None

    def map(self, x: Sequence[Any]) -> Sequence[Any]:
        """
        Identity map

        Notes
        -----
        Identity scales bypass the palette completely since the
        map is the identity function.
        """
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


# American to British spelling
alias("scale_colour_identity", scale_color_identity)

from __future__ import annotations

from dataclasses import KW_ONLY, dataclass
from typing import TYPE_CHECKING, Literal

from .._utils.registry import alias
from .scale_continuous import scale_continuous
from .scale_discrete import scale_discrete

if TYPE_CHECKING:
    from typing import Any, Sequence


class MapTrainMixin:
    """
    Override map and train methods
    """

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
        if self.guide is None:  # pyright: ignore
            return

        return super().train(x)  # pyright: ignore


@dataclass
class scale_color_identity(MapTrainMixin, scale_discrete):
    """
    No color scaling
    """

    _aesthetics = ["color"]


@dataclass
class scale_fill_identity(scale_color_identity):
    """
    No color scaling
    """

    _aesthetics = ["fill"]


@dataclass
class scale_shape_identity(MapTrainMixin, scale_discrete):
    """
    No shape scaling
    """

    _aesthetics = ["shape"]


@dataclass
class scale_linetype_identity(MapTrainMixin, scale_discrete):
    """
    No linetype scaling
    """

    _aesthetics = ["linetype"]


@dataclass
class scale_alpha_identity(
    MapTrainMixin, scale_continuous[Literal["legend"] | None]
):
    """
    No alpha scaling
    """

    _aesthetics = ["alpha"]
    _: KW_ONLY
    guide: Literal["legend"] | None = "legend"


@dataclass
class scale_size_identity(
    MapTrainMixin, scale_continuous[Literal["legend"] | None]
):
    """
    No size scaling
    """

    _aesthetics = ["size"]
    _: KW_ONLY
    guide: Literal["legend"] | None = "legend"


# American to British spelling
@alias
class scale_colour_identity(scale_color_identity):
    pass

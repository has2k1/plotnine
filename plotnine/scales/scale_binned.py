from __future__ import annotations

from dataclasses import dataclass, field, is_dataclass, replace
from inspect import Parameter, signature
from typing import TYPE_CHECKING, TypeVar, cast
from warnings import warn

import numpy as np
import pandas as pd
from mizani.bounds import squish

from ..exceptions import PlotnineError, PlotnineWarning
from ._runtime_typing import MinorBreaksUser, OptionalBinnedGuide
from .scale_continuous import scale_continuous

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from mizani.typing import PCensor
    from numpy.typing import NDArray

    from plotnine.typing import FloatArrayLike

T = TypeVar("T")


@dataclass(frozen=True)
class _BinPartition:
    """A continuous scale range divided into numeric bins"""

    limits: tuple[float, float]
    breaks: NDArray[np.float64]
    boundaries: NDArray[np.float64]
    midpoints: NDArray[np.float64]

    @classmethod
    def make(
        cls,
        scale: scale_binned,
        limits: tuple[float, float] | None = None,
    ) -> _BinPartition:
        """Resolve the scale limits and resulting bin geometry"""
        if limits is None:
            limits = scale.final_limits

        breaks = np.asarray(scale._resolve_breaks(limits), dtype=float)
        breaks = breaks[np.isfinite(breaks)]
        low, high = sorted(limits)
        breaks = breaks[(breaks >= low) & (breaks <= high)]

        if scale.limits is None:
            data_limits = np.sort(
                np.asarray(scale.inverse(limits), dtype=float)
            )
            data_breaks = np.sort(
                np.asarray(scale.inverse(breaks), dtype=float)
            )
            data_breaks = data_breaks[
                (data_breaks > data_limits[0]) & (data_breaks < data_limits[1])
            ]
            if len(data_breaks) >= 2:
                data_limits = np.array(
                    [
                        2 * data_breaks[0] - data_breaks[1],
                        2 * data_breaks[-1] - data_breaks[-2],
                    ]
                )
            elif len(data_breaks) == 1:
                width = max(
                    data_breaks[0] - data_limits[0],
                    data_limits[1] - data_breaks[0],
                )
                data_limits = data_breaks[0] + np.array([-width, width])
            elif data_limits[0] == data_limits[1]:
                data_limits = data_limits + np.array([-0.05, 0.05])

            adjusted = np.asarray(scale.transform(data_limits), dtype=float)
            if np.all(np.isfinite(adjusted)):
                low, high = sorted(adjusted)
                limits = (float(low), float(high))

        breaks = breaks[(breaks >= limits[0]) & (breaks <= limits[1])]
        boundaries = np.unique(np.concatenate((limits, breaks)))

        if len(boundaries) < 2:
            raise PlotnineError(
                "Binned scales require at least two distinct finite "
                "boundaries."
            )

        interior = boundaries[
            (boundaries > boundaries[0]) & (boundaries < boundaries[-1])
        ]
        midpoints = boundaries[:-1] + np.diff(boundaries) / 2
        return cls(
            limits=(float(boundaries[0]), float(boundaries[-1])),
            breaks=interior,
            boundaries=boundaries,
            midpoints=midpoints,
        )


def binned_pal(
    palette: Callable[[int], Sequence[T]],
) -> Callable[[Sequence[float]], Sequence[T]]:
    """Adapt a count-based palette to binned midpoint values"""

    def _palette(midpoints: Sequence[float]) -> Sequence[T]:
        return palette(len(midpoints))

    return _palette


@dataclass(kw_only=True)
class scale_binned(scale_continuous[OptionalBinnedGuide]):
    """Base class for mapping continuous data through numeric bins"""

    n_breaks: int | None = None
    """Number of interior breaks to generate automatically"""

    nice_breaks: bool = True
    """Whether to generate breaks at easy-to-read values"""

    right: bool = True
    """Whether each boundary value belongs to the lower bin"""

    show_limits: bool = False
    """Whether guides should label both scale limits"""

    minor_breaks: MinorBreaksUser = None
    guide: OptionalBinnedGuide = "bins"
    oob: PCensor = squish

    _partition: _BinPartition | None = field(
        init=False, default=None, repr=False
    )

    def __post_init__(self) -> None:
        if self.n_breaks is not None and (
            isinstance(self.n_breaks, bool)
            or not isinstance(self.n_breaks, int)
            or self.n_breaks <= 0
        ):
            raise PlotnineError("`n_breaks` must be a positive integer.")
        super().__post_init__()

    def train(self, x: FloatArrayLike) -> None:
        """Train the continuous range and discard its resolved bins"""
        values = np.asarray(x)
        if values.dtype.kind not in "iufc":
            raise PlotnineError("Binned scales only support continuous data.")
        super().train(x)
        self._partition = None

    def _resolve_breaks(self, limits: tuple[float, float]) -> Sequence[float]:
        data_limits = cast("tuple[float, float]", self.inverse(limits))
        if self.is_empty() or self.breaks is False or self.breaks is None:
            return []
        if self.breaks is True:
            if self.nice_breaks:
                provider = self._trans.breaks_func
                if self.n_breaks is None:
                    breaks = self._trans.breaks(data_limits)
                elif is_dataclass(provider) and hasattr(provider, "n"):
                    updated = cast(
                        "Callable[..., Sequence[float]]",
                        replace(provider, n=self.n_breaks),
                    )
                    breaks = updated(data_limits)
                elif self._accepts_n(cast("Callable[..., object]", provider)):
                    breaks = cast("Callable[..., Sequence[float]]", provider)(
                        data_limits, n=self.n_breaks
                    )
                else:
                    self._warn_ignored_n_breaks("transformation")
                    breaks = self._trans.breaks(data_limits)
            else:
                n = self.n_breaks or 5
                breaks = np.linspace(*data_limits, n + 2)[1:-1]
        elif callable(self.breaks):
            if self._accepts_n(self.breaks):
                breaks = self.breaks(data_limits, n=self.n_breaks or 5)
            else:
                if self.n_breaks is not None:
                    self._warn_ignored_n_breaks("breaks callable")
                breaks = self.breaks(data_limits)
        else:
            breaks = self.breaks
        return cast("Sequence[float]", self.transform(breaks))

    @staticmethod
    def _accepts_n(func: Callable[..., object]) -> bool:
        parameters = signature(func).parameters.values()
        return any(
            parameter.name == "n" or parameter.kind is Parameter.VAR_KEYWORD
            for parameter in parameters
        )

    def _warn_ignored_n_breaks(self, provider: str) -> None:
        warn(
            f"Ignoring `n_breaks` because the {provider} does not accept an "
            "`n` argument.",
            PlotnineWarning,
            stacklevel=3,
        )

    def _resolve_partition(
        self, limits: tuple[float, float] | None = None
    ) -> _BinPartition:
        """Return the resolved bins for the current scale state"""
        if limits is not None:
            return _BinPartition.make(self, limits)
        if self._partition is None:
            self._partition = _BinPartition.make(self)
        return self._partition

    def map(
        self,
        x: FloatArrayLike,
        limits: tuple[float, float] | None = None,
    ) -> FloatArrayLike:
        """Map each continuous value to its bin's aesthetic value"""
        partition = self._resolve_partition(limits)
        values = np.asarray(
            self.oob(np.asarray(x, dtype=float), partition.limits),
            dtype=float,
        )
        missing = pd.isna(values)
        bin_numbers = np.digitize(
            values,
            partition.breaks,
            right=self.right,
        )
        positions = self.rescaler(
            partition.midpoints,
            _from=partition.limits,
        )
        palette = np.asarray(self.palette(positions))
        scaled = palette[np.clip(bin_numbers, 0, len(palette) - 1)]
        if scaled.dtype.kind in "US":
            result = scaled.astype(object)
        else:
            result = scaled.copy()
        result[missing] = self.na_value
        return result

    def get_breaks(
        self, limits: tuple[float, float] | None = None
    ) -> Sequence[float]:
        """Return the transformed boundaries between bins"""
        if self.breaks is False or self.breaks is None:
            return []
        return self._resolve_partition(limits).breaks.tolist()

    def get_minor_breaks(
        self,
        major: Sequence[float],
        limits: tuple[float, float] | None = None,
    ) -> Sequence[float]:
        """Return no minor breaks for a binned scale"""
        return []

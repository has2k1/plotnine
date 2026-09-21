from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass, field, is_dataclass, replace
from inspect import Parameter, signature
from typing import TYPE_CHECKING, Any, Protocol, TypeVar, cast
from warnings import warn

import numpy as np
import pandas as pd
from mizani.bounds import squish

from ..exceptions import PlotnineError, PlotnineWarning
from ._runtime_typing import MinorBreaksUser, OptionalBinnedGuide
from .scale_continuous import scale_continuous

if TYPE_CHECKING:
    from collections.abc import Callable

    from mizani.typing import PCensor
    from numpy.typing import NDArray

    from plotnine.typing import FloatArray, FloatArrayLike

    from .scale import scale

T_co = TypeVar("T_co", covariant=True)


# Match finite numeric interval strings such as `(1, 2]` for binned guides.
_INTERVAL_RE = re.compile(
    r"^\s*[\[(]\s*"
    r"(?P<left>[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?)"
    r"\s*,\s*"
    r"(?P<right>[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?)"
    r"\s*[\])]\s*$"
)


@dataclass(kw_only=True)
class scale_binned(scale_continuous[OptionalBinnedGuide]):
    """Base class for mapping continuous data through numeric bins"""

    n_breaks: int | None = None
    """Number of interior breaks to generate automatically"""

    nice_breaks: bool = True
    """
    Whether to generate breaks at easy-to-read values

    When `True`, `n_breaks` is a suggestion. When `False`, the scale
    creates exactly `n_breaks` evenly spaced interior breaks.
    """

    right: bool = True
    """Whether each bin includes its right boundary and excludes its left"""

    show_limits: bool = False
    """Whether guides should label both scale limits"""

    minor_breaks: MinorBreaksUser = None
    guide: OptionalBinnedGuide = "bins"
    oob: PCensor = squish

    _intervals: _BinIntervals | None = field(
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
        """Train the continuous range and discard its resolved intervals"""
        values = np.asarray(x)
        if values.dtype.kind not in "iufc":
            raise PlotnineError("Binned scales only support continuous data.")
        super().train(x)
        self._intervals = None

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

    def _breaks_at_limits(
        self,
        limits: tuple[float, float],
    ) -> tuple[bool, bool]:
        """Report whether fixed breaks coincide with either scale limit"""
        breaks = self._fixed_breaks()
        if breaks is None:
            return False, False

        return (
            bool(np.any(np.isclose(breaks, limits[0]))),
            bool(np.any(np.isclose(breaks, limits[1]))),
        )

    def _fixed_breaks(self) -> NDArray[np.float64] | None:
        """Return transformed fixed breaks when the scale defines them"""
        breaks = self.breaks
        if (
            breaks is True
            or breaks is False
            or breaks is None
            or callable(breaks)
        ):
            return None
        return np.asarray(self.transform(breaks), dtype=float)

    def _resolve_intervals(
        self, limits: tuple[float, float] | None = None
    ) -> _BinIntervals:
        """Return the resolved bin intervals for the current scale state"""
        if limits is not None:
            return _BinIntervals.make(self, limits)
        if self._intervals is None:
            self._intervals = _BinIntervals.make(self)
        return self._intervals

    def map(
        self,
        x: FloatArrayLike,
        limits: tuple[float, float] | None = None,
    ) -> FloatArrayLike:
        """Map each continuous value to its bin's aesthetic value"""
        intervals = self._resolve_intervals(limits)
        values = np.asarray(
            self.oob(np.asarray(x, dtype=float), intervals.limits),
            dtype=float,
        )
        missing = pd.isna(values)
        bin_numbers = np.digitize(
            values,
            intervals.breaks,
            right=self.right,
        )
        positions = self.rescaler(
            intervals.midpoints,
            _from=intervals.limits,
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
        return self._resolve_intervals(limits).breaks.tolist()

    def get_labels(
        self, breaks: Sequence[float] | None = None
    ) -> Sequence[str]:
        """Format labels for bin boundaries and included scale limits"""
        if breaks is None:
            return super().get_labels(breaks)

        labels = self.labels
        if isinstance(labels, Sequence) and not isinstance(labels, str):
            source_breaks = self._fixed_breaks()
            if source_breaks is None:
                source_breaks = np.asarray(self.get_breaks(), dtype=float)
            has_added_break = any(
                not np.any(np.isclose(source_breaks, value))
                for value in breaks
            )
            if has_added_break:
                warn(
                    "Fixed labels do not cover every requested boundary; "
                    "formatting the missing labels.",
                    PlotnineWarning,
                    stacklevel=3,
                )
                formatted = list(self._trans.format(self.inverse(breaks)))
                source_labels = super().get_labels(source_breaks.tolist())
                for value, label in zip(source_breaks, source_labels):
                    index = np.flatnonzero(np.isclose(breaks, value))
                    if len(index):
                        formatted[index[0]] = label
                return formatted

        return super().get_labels(breaks)

    def get_minor_breaks(
        self,
        major: Sequence[float],
        limits: tuple[float, float] | None = None,
    ) -> Sequence[float]:
        """Return no minor breaks for a binned scale"""
        return []


class _BinnedPalette(Protocol[T_co]):
    def __call__(self, x: Sequence[float]) -> Sequence[T_co]: ...


@dataclass(frozen=True)
class _BinIntervals:
    """Resolved numeric intervals for a trained scale"""

    limits: tuple[float, float]
    breaks: FloatArray
    boundaries: FloatArray
    midpoints: FloatArray
    source_values: FloatArray | Sequence[Any]
    explicit_limits: tuple[bool, bool]

    @classmethod
    def make(
        cls,
        scale: scale,
        limits: tuple[float, float] | None = None,
    ) -> _BinIntervals:
        """Resolve numeric bin intervals from a trained scale"""
        if not isinstance(scale, scale_binned):
            # A binned guide can represent a non-binned scale only when its
            # trained values describe contiguous intervals.
            values = list(scale.final_limits)
            intervals = [_as_interval(value) for value in values]
            if not intervals:
                raise PlotnineError("Invalid interval breaks: no intervals.")

            left = np.asarray([x[0] for x in intervals], dtype=float)
            right = np.asarray([x[1] for x in intervals], dtype=float)
            if np.any(left >= right) or not np.allclose(left[1:], right[:-1]):
                raise PlotnineError(
                    "Invalid interval breaks: intervals must be contiguous "
                    "and non-overlapping."
                )

            boundaries = np.concatenate((left[:1], right))
            return cls(
                limits=(float(boundaries[0]), float(boundaries[-1])),
                breaks=boundaries[1:-1],
                boundaries=boundaries,
                midpoints=left + (right - left) / 2,
                source_values=values,
                explicit_limits=(False, False),
            )

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
            source_values=midpoints,
            explicit_limits=scale._breaks_at_limits(
                (float(boundaries[0]), float(boundaries[-1]))
            ),
        )

    def get_breaks(self, show_limits: bool) -> NDArray[np.float64]:
        """Return labelled interior boundaries and included scale limits"""
        include_lower = show_limits or self.explicit_limits[0]
        include_upper = show_limits or self.explicit_limits[1]
        values = self.breaks
        if include_lower:
            values = np.concatenate((self.boundaries[:1], values))
        if include_upper:
            values = np.concatenate((values, self.boundaries[-1:]))
        return np.asarray(values, dtype=float)


def _as_interval(value: pd.Interval | str) -> tuple[float, float]:
    """Extract the numeric endpoints from an interval value"""
    if isinstance(value, pd.Interval):
        try:
            return float(value.left), float(value.right)
        except (TypeError, ValueError) as err:
            raise PlotnineError(
                f"Invalid interval breaks: {value!r}."
            ) from err

    if isinstance(value, str) and (match := _INTERVAL_RE.match(value)):
        return float(match["left"]), float(match["right"])

    raise PlotnineError(f"Invalid interval breaks: {value!r}.")


def binned_pal(
    palette: Callable[[int], Sequence[T_co]],
) -> _BinnedPalette[T_co]:
    """Adapt a count-based palette to binned midpoint values"""

    def _palette(x: Sequence[float]) -> Sequence[T_co]:
        return palette(len(x))

    return _palette

"""
This module contains type aliases needed in plotnine.scales.* at runtime.
For example as annotations when declaring dataclasses. They are separated
out so that we can refer to them as plotnine.scales._runtime_typing for
the documentation.
"""

from typing import Callable, Sequence, Type, TypeAlias, TypeVar

from mizani.transforms import trans

from .range import Range

# fmt: off

DiscreteBreaksUser: TypeAlias = (
    bool
    | None
    | Sequence[str]
    | Callable[[Sequence[str]], Sequence[str]]
)

DiscreteLimitsUser: TypeAlias = (
    None
    | Sequence[str]
    | Callable[[Sequence[str]], Sequence[str]]
)

ContinuousBreaksUser: TypeAlias = (
    bool
    | None
    | Sequence[float]
    | Callable[[tuple[float, float]], Sequence[float]]
)

MinorBreaksUser: TypeAlias = ContinuousBreaksUser

ContinuousLimitsUser: TypeAlias = (
    None
    | tuple[float, float]
    | Callable[[tuple[float, float]], tuple[float, float]]
)

ScaleLabelsUser: TypeAlias = (
    bool
    | None
    | Sequence[str]
    | Callable[[Sequence[float] | Sequence[str]], Sequence[str]]
    | dict[str, str]
)

TransUser: TypeAlias = trans | str | Type[trans] | None

RangeT = TypeVar("RangeT", bound=Range)
BreaksUserT = TypeVar("BreaksUserT")
LimitsUserT = TypeVar("LimitsUserT")
GuideTypeT = TypeVar("GuideTypeT")

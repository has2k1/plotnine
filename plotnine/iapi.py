"""
Internal API

Specifications for containers that will hold different kinds
of objects with data that is created when the plot is being
built.
"""
from __future__ import annotations

import typing
from dataclasses import dataclass, fields
from typing import Any, Iterator, List, Optional, Sequence

if typing.TYPE_CHECKING:
    import plotnine as p9


@dataclass
class scale_view:
    """
    Scale information after it has been trained
    """
    scale: p9.scales.scale.scale
    aesthetics: List[str]
    name: str
    # Trainned limits of the scale
    limits: tuple[float, float]
    # Physical size of scale, including expansions
    range: tuple[float, float]
    breaks: Sequence[float] | dict[str, Any]
    minor_breaks: Sequence[float]
    labels: Sequence[str]


@dataclass
class range_view:
    """
    Range information after trainning
    """
    range: tuple[float, float]
    range_coord: tuple[float, float]


@dataclass
class labels_view:
    """
    Scale labels (incl. caption & title) for the plot
    """
    x: Optional[str] = None
    y: Optional[str] = None
    alpha: Optional[str] = None
    color: Optional[str] = None
    colour: Optional[str] = None
    fill: Optional[str] = None
    linetype: Optional[str] = None
    shape: Optional[str] = None
    size: Optional[str] = None
    stroke: Optional[str] = None
    title: Optional[str] = None
    caption: Optional[str] = None

    def update(self, other: labels_view) -> None:
        """
        Update the labels with those in other
        """
        for name, value in other.iter_set_fields():
            setattr(self, name, value)

    def add_defaults(self, other: labels_view) -> None:
        """
        Update labels that are missing with those in other
        """
        for name, value in other.iter_set_fields():
            cur_value = getattr(self, name)
            if cur_value is None:
                setattr(self, name, value)

    def iterfields(self) -> Iterator[tuple[str, Optional[str]]]:
        """
        Return an iterator of all (field, value) pairs
        """
        return ((f.name, getattr(self, f.name)) for f in fields(self))

    def iter_set_fields(self) -> Iterator[tuple[str, str]]:
        """
        Return an iterator of (field, value) pairs of none None values
        """
        return ((k, v) for k, v in self.iterfields() if v is not None)

    def get(self, name: str, default: str) -> str:
        """
        Get label value, return default if value is None
        """
        value = getattr(self, name)
        return str(value) if value is not None else default

    def __contains__(self, name: str) -> bool:
        """
        Return True if name has been set (is not None)
        """
        return getattr(self, name) is not None

    def __repr__(self) -> str:
        """
        Representations without the None values
        """
        nv_pairs = ", ".join(
            f"{name}={repr(value)}"
            for name, value in self.iter_set_fields()
        )
        return f"{self.__class__.__name__}({nv_pairs})"


@dataclass
class panel_view:
    """
    Information from the trained position scales in a panel
    """
    x: scale_view
    y: scale_view


@dataclass
class panel_ranges:
    """
    Ranges for the panel
    """
    x: tuple[float, float]
    y: tuple[float, float]


@dataclass
class pos_scales:
    """
    Position Scales
    """
    x: p9.scales.scale.scale
    y: p9.scales.scale.scale

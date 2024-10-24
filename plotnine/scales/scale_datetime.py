from __future__ import annotations

from dataclasses import KW_ONLY, InitVar, dataclass

from ._runtime_typing import TransUser  # noqa: TCH001
from .scale_continuous import scale_continuous


@dataclass
class scale_datetime(scale_continuous):
    """
    Base class for all date/datetime scales
    """

    date_breaks: InitVar[str | None] = None
    """
    A string giving the distance between major breaks.
    For example `'2 weeks'`, `'5 years'`. If specified,
    `date_breaks` takes precedence over
    `breaks`.
    """

    date_labels: InitVar[str | None] = None
    """
    Format string for the labels.
    See [strftime](:ref:`strftime-strptime-behavior`).
    If specified, `date_labels` takes precedence over
    `labels`.
    """

    date_minor_breaks: InitVar[str | None] = None
    """
    A string giving the distance between minor breaks.
    For example `'2 weeks'`, `'5 years'`. If specified,
    `date_minor_breaks` takes precedence over
    `minor_breaks`.
    """

    _: KW_ONLY
    trans: TransUser = "datetime"

    def __post_init__(
        self,
        date_breaks: str | None,
        date_labels: str | None,
        date_minor_breaks: str | None,
    ):
        from mizani.breaks import breaks_date as breaks_func
        from mizani.labels import label_date as labels_func

        if date_breaks is not None:
            self.breaks = breaks_func(date_breaks)  # pyright: ignore
        elif isinstance(self.breaks, str):
            self.breaks = breaks_func(width=self.breaks)  # pyright: ignore

        if date_labels is not None:
            self.labels = labels_func(date_labels)  # pyright: ignore
        elif isinstance(self.labels, str):
            self.labels = labels_func(width=self.labels)  # pyright: ignore

        if date_minor_breaks is not None:
            self.minor_breaks = breaks_func(date_minor_breaks)  # pyright: ignore
        elif isinstance(self.minor_breaks, str):
            self.minor_breaks = breaks_func(width=self.minor_breaks)  # pyright: ignore

        scale_continuous.__post_init__(self)

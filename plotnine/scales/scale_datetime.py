from __future__ import annotations

from dataclasses import KW_ONLY, InitVar, dataclass
from typing import TYPE_CHECKING
from warnings import warn

from ._runtime_typing import TransUser  # noqa: TCH001
from .scale_continuous import scale_continuous

if TYPE_CHECKING:
    from datetime import timedelta


@dataclass
class scale_datetime(scale_continuous):
    """
    Base class for all date/datetime scales
    """

    date_breaks: InitVar[str | None] = None
    """
    A string giving the distance between major breaks.
    For example `'2 weeks'`, `'5 years'`. If specified,
    `date_breaks` takes precedence over `breaks`.
    """

    date_labels: InitVar[str | None] = None
    """
    Format string for the labels.
    See [strftime](:ref:`strftime-strptime-behavior`).
    If specified, `date_labels` takes precedence over `labels`.
    """

    date_minor_breaks: InitVar[str | None] = None
    """
    A string giving the distance between minor breaks.
    For example `'2 weeks'`, `'5 years'`. If specified,
    `date_minor_breaks` takes precedence over `minor_breaks`.
    """

    _: KW_ONLY
    trans: TransUser = "datetime"
    # fmt: off
    expand: ( # pyright: ignore[reportIncompatibleVariableOverride]
        tuple[float, timedelta]
        | tuple[float, timedelta, float, timedelta]
        | None
    ) = None
    # fmt: on
    """
    Multiplicative and additive expansion constants
    that determine how the scale is expanded. If
    specified must be of length 2 or 4. Specifically the
    values are in this order:

    ```
    (mul, add)
    (mul_low, add_low, mul_high, add_high)
    ```

    For example,

    - `(0, timedelta(0))` - Do not expand.
    - `(0, timedelta(days=1))` - Expand lower and upper limits by 1 day.
    - `(1, 0)` - Expand lower and upper limits by 100%.
    - `(0, 0, 0, timedelta(hours=6))` - Expand upper limit by 6 hours.
    - `(0, timedelta(minutes=5), 0.1, timdelta(0))` - Expand lower limit
      by 5 minutes and upper limit by 10%.
    - `(0, 0, 0.1, timedelta(weeks=2))` - Expand upper limit by 10% plus
      2 weeks.

    If not specified, suitable defaults are chosen.
    """

    def __post_init__(
        self,
        date_breaks: str | None,
        date_labels: str | None,
        date_minor_breaks: str | None,
    ):
        from mizani.breaks import breaks_date_width
        from mizani.labels import label_date

        if date_breaks is not None:
            self.breaks = breaks_date_width(date_breaks)  # pyright: ignore[reportAttributeAccessIssue]
        elif isinstance(self.breaks, str):
            warn(
                "Passing a string to `breaks` will not work in "
                f"future versions. Use `date_breaks={self.breaks!r}`",
                FutureWarning,
            )
            self.breaks = breaks_date_width(width=self.breaks)  # pyright: ignore[reportAttributeAccessIssue]

        if date_labels is not None:
            self.labels = label_date(fmt=date_labels)  # pyright: ignore[reportAttributeAccessIssue]
        elif isinstance(self.labels, str):
            warn(
                "Passing a string to `labels` will not work in "
                f"future versions. Use `date_labels={self.labels!r}`",
                FutureWarning,
            )
            self.labels = label_date(fmt=self.labels)  # pyright: ignore[reportAttributeAccessIssue]

        if date_minor_breaks is not None:
            self.minor_breaks = breaks_date_width(date_minor_breaks)  # pyright: ignore[reportAttributeAccessIssue]
        elif isinstance(self.minor_breaks, str):
            warn(
                "Passing a string to `minor_breaks` will not work in "
                "future versions. "
                f"Use `date_minor_breaks={self.minor_breaks!r}`",
                FutureWarning,
            )
            self.minor_breaks = breaks_date_width(width=self.minor_breaks)  # pyright: ignore[reportAttributeAccessIssue]

        scale_continuous.__post_init__(self)

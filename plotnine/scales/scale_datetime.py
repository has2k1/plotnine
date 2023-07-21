from __future__ import annotations

from contextlib import suppress

from ..doctools import document
from .scale_continuous import scale_continuous


@document
class scale_datetime(scale_continuous):
    """
    Base class for all date/datetime scales

    Parameters
    ----------
    date_breaks : str
        A string giving the distance between major breaks.
        For example `'2 weeks'`, `'5 years'`. If specified,
        ``date_breaks`` takes precedence over
        ``breaks``.
    date_labels : str
        Format string for the labels.
        See :ref:`strftime <strftime-strptime-behavior>`.
        If specified, ``date_labels`` takes precedence over
        ``labels``.
    date_minor_breaks : str
        A string giving the distance between minor breaks.
        For example `'2 weeks'`, `'5 years'`. If specified,
        ``date_minor_breaks`` takes precedence over
        ``minor_breaks``.
    {superclass_parameters}
    """

    _trans = "datetime"

    def __init__(self, **kwargs):
        from mizani.breaks import date_breaks
        from mizani.formatters import date_format

        # Permit the use of the general parameters for
        # specifying the format strings
        with suppress(KeyError):
            breaks = kwargs["breaks"]
            if isinstance(breaks, str):
                kwargs["breaks"] = date_breaks(breaks)

        with suppress(KeyError):
            minor_breaks = kwargs["minor_breaks"]
            if isinstance(minor_breaks, str):
                kwargs["minor_breaks"] = date_breaks(minor_breaks)

        # Using the more specific parameters take precedence
        with suppress(KeyError):
            breaks_fmt = kwargs.pop("date_breaks")
            kwargs["breaks"] = date_breaks(breaks_fmt)

        with suppress(KeyError):
            labels_fmt = kwargs.pop("date_labels")
            kwargs["labels"] = date_format(labels_fmt)

        with suppress(KeyError):
            minor_breaks_fmt = kwargs.pop("date_minor_breaks")
            kwargs["minor_breaks"] = date_breaks(minor_breaks_fmt)

        scale_continuous.__init__(self, **kwargs)

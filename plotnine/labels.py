from __future__ import annotations

from dataclasses import dataclass, fields
from typing import TYPE_CHECKING

from .iapi import labels_view
from .mapping.aes import rename_aesthetics

if TYPE_CHECKING:
    import plotnine as p9

__all__ = ("xlab", "ylab", "labs", "ggtitle")


@dataclass
class labs:
    """
    Add labels for any aesthetics with a scale or title, subtitle & caption
    """

    # Names of Scaled Aesthetics
    x: str | None = None
    y: str | None = None
    alpha: str | None = None
    color: str | None = None
    colour: str | None = None
    fill: str | None = None
    linetype: str | None = None
    shape: str | None = None
    size: str | None = None
    stroke: str | None = None

    # Other texts
    title: str | None = None
    subtitle: str | None = None
    caption: str | None = None

    def __post_init__(self):
        kwargs: dict[str, str] = {
            f.name: value
            for f in fields(self)
            if (value := getattr(self, f.name)) is not None
        }
        self.labels = labels_view(**rename_aesthetics(kwargs))

    def __radd__(self, plot: p9.ggplot) -> p9.ggplot:
        """
        Add labels to ggplot object
        """
        plot.labels.update(self.labels)
        return plot


class xlab(labs):
    """
    Label/name for the x aesthetic

    Parameters
    ----------
    name :
        x aesthetic label (x-axis)
    """

    def __init__(self, name: str, /):
        self.x = name
        self.labels = labels_view(x=name)


class ylab(labs):
    """
    Label/name for the y aesthetic

    Parameters
    ----------
    name :
        y aesthetic label i.e. y-axis label
    """

    def __init__(self, name: str, /):
        self.y = name
        self.labels = labels_view(y=name)


class ggtitle(labs):
    """
    Create plot title

    Parameters
    ----------
    title :
        Plot title
    """

    def __init__(self, title: str, /):
        self.title = title
        self.labels = labels_view(title=title)

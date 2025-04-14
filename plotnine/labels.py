from __future__ import annotations

from dataclasses import dataclass, fields
from typing import TYPE_CHECKING

from .iapi import labels_view
from .mapping.aes import rename_aesthetics

if TYPE_CHECKING:
    import plotnine as p9

__all__ = ("xlab", "ylab", "labs", "ggtitle")


# TODO: Make keyword-only when python>=3.10
# i.e. @dataclass(kw_only=True)
@dataclass
class labs:
    """
    Add labels for any aesthetics with a scale or title, subtitle & caption
    """

    # Names of Scaled Aesthetics
    x: str | None = None
    """
    Name of the x-axis.
    """

    y: str | None = None
    """
    Name of the y-axis.
    """

    alpha: str | None = None
    """
    Name of the alpha legend.
    """

    color: str | None = None
    """
    Name of the color legend or colorbar.
    """

    colour: str | None = None
    """
    Name of the colour legend or colourbar.

    This is an alias of the `color` parameter. Only use one of
    the spellings.
    """

    fill: str | None = None
    """
    Name of the fill legend/colourbar.
    """

    linetype: str | None = None
    """
    Name of the linetype legend.
    """

    shape: str | None = None
    """
    Name of the shape legend.
    """

    size: str | None = None
    """
    Name of the size legend.
    """

    stroke: str | None = None
    """
    Name of the stroke legend.
    """

    # Other texts
    title: str | None = None
    """
    The title of the plot.
    """

    subtitle: str | None = None
    """
    The subtitle of the plot.
    """

    caption: str | None = None
    """
    The caption at the bottom of the plot.
    """

    tag: str | None = None
    """
    A plot tag
    """

    def __post_init__(self):
        kwargs: dict[str, str] = {
            f.name: value
            for f in fields(self)
            if (value := getattr(self, f.name)) is not None
        }
        self.labels = labels_view(**rename_aesthetics(kwargs))

    def __radd__(self, other: p9.ggplot) -> p9.ggplot:
        """
        Add labels to ggplot object
        """
        other.labels.update(self.labels)
        return other


class xlab(labs):
    """
    Label/name for the x aesthetic

    Parameters
    ----------
    name :
        x aesthetic label (x-axis)
    """

    def __init__(self, label: str):
        super().__init__(x=label)


class ylab(labs):
    """
    Label/name for the y aesthetic

    Parameters
    ----------
    name :
        y aesthetic label i.e. y-axis label
    """

    def __init__(self, label: str):
        super().__init__(y=label)


class ggtitle(labs):
    """
    Create plot title

    Parameters
    ----------
    title :
        Plot title
    """

    def __init__(self, title: str | None = None, subtitle: str | None = None):
        super().__init__(title=title, subtitle=subtitle)

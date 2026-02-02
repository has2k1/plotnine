from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .. import theme
from .._utils.dataclasses import non_none_init_items
from ..composition._types import ComposeAddable

if TYPE_CHECKING:
    from ._compose import Compose


@dataclass(kw_only=True)
class plot_annotation(ComposeAddable):
    """
    Annotate a composition

    This applies to only the top-level composition. When a composition
    with an annotation is added to larger composition, the annotation
    of the sub-composition becomes irrelevant.
    """

    title: str | None = None
    """
    The title of the composition
    """

    subtitle: str | None = None
    """
    The subtitle of the composition
    """

    caption: str | None = None
    """
    The caption of the composition
    """

    footer: str | None = None
    """
    The footer of the composition
    """

    theme: theme = field(default_factory=theme)  # pyright: ignore[reportUnboundVariable]
    """
    Theme for the plot title, subtitle, caption, footer, margin and background

    It also controls the [](`~plotnine.themes.themeables.figure_size`) of the
    composition. The default theme is the same as the default one used for the
    plots, which you can change with [](`~plotnine.theme_set`).
    """

    def __radd__(self, cmp: Compose) -> Compose:
        """
        Add plot annotation to composition
        """
        cmp.annotation = self
        return cmp

    def update(self, other: plot_annotation):
        """
        Update this annotation with the contents of other
        """
        for name, value in non_none_init_items(other):
            if name == "theme":
                self.theme = self.theme + value
            else:
                setattr(self, name, value)

    def empty(self) -> bool:
        """
        Whether the annotation has any content
        """
        for name, value in non_none_init_items(self):
            if name == "theme":
                return len(value.themeables) == 0
            else:
                return False

        return True

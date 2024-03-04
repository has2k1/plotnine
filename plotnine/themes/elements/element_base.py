"""
Theme elements used to decorate the graph.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

    from plotnine import theme


class element_base:
    """
    Base class for all theme elements
    """

    properties: dict[str, Any]  # dict of the properties

    def __init__(self):
        self.properties = {"visible": True}

    def __repr__(self) -> str:
        """
        Element representation
        """
        return f"{self.__class__.__name__}({self})"

    def __str__(self) -> str:
        """
        Element as string
        """
        d = self.properties.copy()
        del d["visible"]
        return f"{d}"

    def setup(self, theme: theme, themeable_name: str):
        """
        Setup the theme_element before drawing
        """

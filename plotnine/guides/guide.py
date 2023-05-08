from __future__ import annotations

import typing

from ..exceptions import PlotnineError
from ..utils import Registry

if typing.TYPE_CHECKING:
    from typing import Any, Literal, Optional

    import pandas as pd

    from plotnine.typing import Scale, Theme


class guide(metaclass=Registry):
    """
    Base class for all guides

    Parameters
    ----------
    title : str | None
        Title of the guide. If ``None``, title is not shown.
        Default is the name of the aesthetic or the name
        specified using :class:`~plotnine.components.labels.lab`
    title_position : str in ``['top', 'bottom', 'left', 'right']``
        Position of title
    title_theme : element_text
        Control over the title theme.
        Default is to use ``legend_title`` in a theme.
    title_hjust : float
        Horizontal justification of title text.
    title_vjust : float
        Vertical justification of title text.
    title_separation : float
        Separation between the title text and the colorbar.
        Value is in pixels.
    label : bool
        Whether to show labels
    label_position : str in ``['top', 'bottom', 'left', 'right']``
        Position of the labels.
        The defaults are ``'bottom'`` for a horizontal guide and
        '``right``' for a vertical guide.
    label_theme : element_text
        Control over the label theme.
        Default is to use ``legend_text`` in a theme.
    label_hjust : float
        Horizontal justification of label text.
    label_vjust : float
        Vertical justification of label text.
    label_separation : float
        Separation between the label text and the colorbar.
        Value is in pixels.
    direction : str in ``['horizontal', 'vertical']``
        Direction of the guide.
    default_unit : str
        Unit for ``keywidth`` and ``keyheight``
    override_aes : dict
        Aesthetic parameters of legend key.
    reverse : bool
        Whether to reverse the order of the legends.
    order : int
        Order of this guide among multiple guides.
        Should be in the range [0, 99]. Default is ``0``.

    Notes
    -----
    At the moment not all parameters have been fully implemented.
    """

    __base__ = True

    # Must be updated before the draw method is called
    theme: Theme
    key: pd.DataFrame

    # title
    title: str
    title_position: Literal["top", "bottom", "left", "right"]
    title_theme = None
    title_hjust: Optional[float] = None
    title_vjust: Optional[float] = None

    # label
    label = True
    label_position: Literal["top", "bottom", "left", "right"]
    label_theme = None
    label_hjust: Optional[float] = None
    label_vjust: Optional[float] = None

    # general
    direction: Optional[Literal["horizontal", "vertical"]] = None
    default_unit = "line"
    override_aes: dict[str, Any] = {}
    reverse = False
    order = 0

    # Aesthetics covered by the guide
    available_aes: set[str] = set()

    def __init__(self, **kwargs):
        no_default = {"title", "title_position", "label_position"}
        for k, v in kwargs.items():
            if hasattr(self, k) or k in no_default:
                setattr(self, k, v)
            else:
                tpl = "{} does not undestand attribute '{}'"
                raise PlotnineError(tpl.format(self.__class__.__name__, k))

    def _set_defaults(self, theme: Theme):
        """
        Set configuration parameters for drawing guide
        """
        self.theme = theme
        valid_locations = {"top", "bottom", "left", "right"}
        _property = theme.themeables.property
        margin_location_lookup = {
            # Where to put the margin between the legend and
            # the axes. Depends on the location of the legend
            "t": "b",
            "b": "t",
            "l": "r",
            "r": "l",
        }

        # label position
        if not hasattr(self, "label_position"):
            self.label_position = "right"

        if self.label_position not in valid_locations:
            msg = "label position '{}' is invalid"
            raise PlotnineError(msg.format(self.label_position))

        # label margin
        # legend_text_legend or legend_text_colorbar
        _legend_type = self.__class__.__name__.split("_")[-1]
        name = "legend_text_{}".format(_legend_type)
        loc = margin_location_lookup[self.label_position[0]]
        margin = _property(name, "margin")
        self._label_margin = margin.get_as(loc, "pt")

        # direction of guide
        if self.direction is None:
            if self.label_position in ("right", "left"):
                self.direction = "vertical"
            else:
                self.direction = "horizontal"

        # title position
        if not hasattr(self, "title_position"):
            if self.direction == "vertical":
                self.title_position = "top"
            elif self.direction == "horizontal":
                self.title_position = "left"
        if self.title_position not in valid_locations:
            msg = "legend title position '{}' is invalid"
            raise PlotnineError(msg.format(self.title_position))

        # title alignment
        self._title_align = _property("legend_title_align")
        if self._title_align == "auto":
            if self.direction == "vertical":
                self._title_align = "left"
            else:
                self._title_align = "center"

        # by default, direction of each guide depends on
        # the position all the guides
        position = _property("legend_position")
        self.direction = _property("legend_direction")
        if self.direction == "auto":
            if position in ("right", "left"):  # default
                self.direction = "vertical"
            else:
                self.direction = "horizontal"

        # title margin
        loc = margin_location_lookup[self.title_position[0]]
        margin = _property("legend_title", "margin")
        self._title_margin = margin.get_as(loc, "pt")

        # legend_margin
        self._legend_margin = _property("legend_margin")

        # legend_entry_spacing
        self._legend_entry_spacing_x = _property("legend_entry_spacing_x")
        self._legend_entry_spacing_y = _property("legend_entry_spacing_y")

    def legend_aesthetics(self, layer, plot):
        """
        Return the aesthetics that contribute to the legend

        Parameters
        ----------
        layer : Layer
            Layer whose legend is to be drawn
        plot : ggplot
            Plot object

        Returns
        -------
        matched : list
            List of the names of the aethetics that contribute
            to the legend.
        """
        l = layer
        legend_ae = set(self.key.columns) - {"label"}
        all_ae = (
            l.mapping.keys()
            | (plot.mapping if l.inherit_aes else set())
            | l.stat.DEFAULT_AES.keys()
        )
        geom_ae = l.geom.REQUIRED_AES | l.geom.DEFAULT_AES.keys()
        matched = all_ae & geom_ae & legend_ae
        matched = list(matched - set(l.geom.aes_params))
        return matched

    def train(
        self, scale: Scale, aesthetic: Optional[str] = None
    ) -> guide | None:
        """
        Create the key for the guide

        Returns guide if training is successful
        """
        pass

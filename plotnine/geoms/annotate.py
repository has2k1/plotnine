from __future__ import annotations

import typing

import pandas as pd

from .._utils import is_scalar
from .._utils.registry import Registry
from ..exceptions import PlotnineError
from ..geoms.geom import geom as geom_base_class
from ..mapping import aes
from ..mapping.aes import POSITION_AESTHETICS

if typing.TYPE_CHECKING:
    from typing import Any

    from plotnine import ggplot
    from plotnine.layer import layer


class annotate:
    """
    Create an annotation layer

    Parameters
    ----------
    geom :
        geom to use for annotation, or name of geom (e.g. 'point').
    x :
        Position
    y :
        Position
    xmin :
        Position
    ymin :
        Position
    xmax :
        Position
    ymax :
        Position
    xend :
        Position
    yend :
        Position
    xintercept :
        Position
    yintercept :
        Position
    kwargs :
        Other aesthetics or parameters to the geom.

    Notes
    -----
    The positioning aethetics `x, y, xmin, ymin, xmax, ymax, xend, yend,
    xintercept, yintercept` depend on which `geom` is used.

    You should choose or ignore accordingly.

    All `geoms` are created with `stat="identity"`{.py}.
    """

    _annotation_geom: geom_base_class

    def __init__(
        self,
        geom: str | type[geom_base_class],
        x: float | None = None,
        y: float | None = None,
        xmin: float | None = None,
        xmax: float | None = None,
        xend: float | None = None,
        xintercept: float | None = None,
        ymin: float | None = None,
        ymax: float | None = None,
        yend: float | None = None,
        yintercept: float | None = None,
        **kwargs: Any,
    ):
        variables = locals()

        # position only, and combined aesthetics
        pos_aesthetics = {
            loc: variables[loc]
            for loc in POSITION_AESTHETICS
            if variables[loc] is not None
        }
        aesthetics = pos_aesthetics.copy()
        aesthetics.update(kwargs)

        # Check if the aesthetics are of compatible lengths
        lengths, info_tokens = [], []
        for ae, val in aesthetics.items():
            if is_scalar(val):
                continue
            lengths.append(len(val))
            info_tokens.append((ae, len(val)))

        if len(set(lengths)) > 1:
            details = ", ".join([f"{n} ({l})" for n, l in info_tokens])
            msg = f"Unequal parameter lengths: {details}"
            raise PlotnineError(msg)

        # Stop pandas from complaining about all scalars
        if all(is_scalar(val) for val in pos_aesthetics.values()):
            for ae in pos_aesthetics:
                pos_aesthetics[ae] = [pos_aesthetics[ae]]
                break

        data = pd.DataFrame(pos_aesthetics)
        if isinstance(geom, str):
            geom_klass: type[geom_base_class] = Registry[f"geom_{geom}"]
        elif isinstance(geom, type) and issubclass(geom, geom_base_class):
            geom_klass = geom
        else:
            raise PlotnineError(
                "geom must either be a plotnine.geom.geom() "
                "descendant (e.g. plotnine.geom_point), or "
                "a string naming a geom (e.g. 'point', 'text', "
                f"...). Got {repr(geom)}"
            )

        mappings = aes(**{str(ae): ae for ae in data.columns})

        # The positions are mapped, the rest are manual settings
        self._annotation_geom = geom_klass(
            mappings,
            data,
            stat="identity",
            inherit_aes=False,
            show_legend=False,
            **kwargs,
        )

    def __radd__(self, plot: ggplot) -> ggplot:
        """
        Add to ggplot
        """
        plot += self.to_layer()  # Add layer
        return plot

    def to_layer(self) -> layer:
        """
        Make a layer that represents this annotation

        Returns
        -------
        out : layer
            Layer
        """
        return self._annotation_geom.to_layer()

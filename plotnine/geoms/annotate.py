from __future__ import annotations

import typing

import numpy as np
import pandas as pd

from .._utils import is_scalar
from .._utils.registry import Registry
from ..exceptions import PlotnineError
from ..geoms.geom import geom as geom_base_class
from ..mapping import aes
from ..mapping._asis import is_asis
from ..mapping.aes import POSITION_AESTHETICS

if typing.TYPE_CHECKING:
    from typing import Any

    from plotnine import ggplot
    from plotnine.mapping._asis import AsIs


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

    Wrap a position aesthetic in [](:func:`~plotnine.I`) to express it as
    a fraction of the panel rather than as a data coordinate.

    All `geoms` are created with `stat="identity"`{.py}.
    """

    _annotation_geom: geom_base_class

    def __init__(
        self,
        geom: str | type[geom_base_class],
        x: float | list[float] | AsIs | None = None,
        y: float | list[float] | AsIs | None = None,
        xmin: float | list[float] | AsIs | None = None,
        xmax: float | list[float] | AsIs | None = None,
        xend: float | list[float] | AsIs | None = None,
        xintercept: float | list[float] | AsIs | None = None,
        ymin: float | list[float] | AsIs | None = None,
        ymax: float | list[float] | AsIs | None = None,
        yend: float | list[float] | AsIs | None = None,
        yintercept: float | list[float] | AsIs | None = None,
        **kwargs: Any,
    ):
        variables = locals()

        # position only, and combined aesthetics
        pos_aesthetics = {
            loc: variables[loc]
            for loc in POSITION_AESTHETICS
            if variables[loc] is not None
        }
        # Record literal positions as expressions after removing their
        # dtype tag so position scales skip them during training.
        asis_aes = {ae for ae, v in pos_aesthetics.items() if is_asis(v)}
        pos_aesthetics = {ae: v for ae, v in pos_aesthetics.items()}
        aesthetics = pos_aesthetics.copy()
        aesthetics.update(kwargs)

        # A length-one position broadcasts to match the other aesthetics.
        lengths, info_tokens = [], []
        for ae, val in aesthetics.items():
            if is_scalar(val):
                continue
            if ae in pos_aesthetics and len(val) == 1:
                continue
            lengths.append(len(val))
            info_tokens.append((ae, len(val)))

        if len(set(lengths)) > 1:
            details = ", ".join([f"{n} ({l})" for n, l in info_tokens])
            msg = f"Unequal parameter lengths: {details}"
            raise PlotnineError(msg)

        # Repeat a length-one position to match the longest position vector.
        if lengths:
            max_length = max(lengths)
            for ae, val in pos_aesthetics.items():
                if not is_scalar(val) and len(val) == 1:
                    pos_aesthetics[ae] = np.repeat(val, max_length)

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

        mappings = aes(
            **{
                str(ae): f"I({ae})" if ae in asis_aes else str(ae)
                for ae in data.columns
            }
        )

        # Map positions and pass the remaining arguments as manual settings.
        self._annotation_geom = geom_klass(
            mappings,
            data,
            stat="identity",
            inherit_aes=False,
            show_legend=False,
            **kwargs,
        )

    def __radd__(self, other: ggplot) -> ggplot:
        """
        Add to ggplot
        """
        from ..layer import layer

        other += layer(geom=self._annotation_geom)
        return other

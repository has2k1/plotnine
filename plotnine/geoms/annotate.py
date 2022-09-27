from copy import deepcopy

import pandas as pd

from ..mapping import aes
from ..mapping.aes import POSITION_AESTHETICS
from ..utils import is_scalar_or_string, Registry
from ..exceptions import PlotnineError
from ..geoms.geom import geom as geom_base_class


class annotate:
    """
    Create an annotation layer

    Parameters
    ----------
    geom : geom or str
        geom to use for annotation, or name of geom (e.g. 'point').
    x : float
        Position
    y : float
        Position
    xmin : float
        Position
    ymin : float
        Position
    xmax : float
        Position
    ymax : float
        Position
    xend : float
        Position
    yend : float
        Position
    xintercept : float
        Position
    yintercept : float
        Position
    kwargs : dict
        Other aesthetics or parameters to the geom.

    Notes
    -----
    The positioning aethetics ``x, y, xmin, ymin, xmax, ymax, xend, yend,
    xintercept, yintercept`` depend on which `geom` is used.

    You should choose or ignore accordingly.

    All `geoms` are created with :code:`stat='identity'`.
    """

    def __init__(
        self,
        geom,
        x=None, y=None,
        xmin=None, xmax=None, xend=None, xintercept=None,
        ymin=None, ymax=None, yend=None, yintercept=None,
        **kwargs
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
            if is_scalar_or_string(val):
                continue
            lengths.append(len(val))
            info_tokens.append((ae, len(val)))

        if len(set(lengths)) > 1:
            details = ', '.join([f'{n} ({l})' for n, l in info_tokens])
            msg = f'Unequal parameter lengths: {details}'
            raise PlotnineError(msg)

        # Stop pandas from complaining about all scalars
        if all(is_scalar_or_string(val) for val in pos_aesthetics.values()):
            for ae in pos_aesthetics.keys():
                pos_aesthetics[ae] = [pos_aesthetics[ae]]
                break

        data = pd.DataFrame(pos_aesthetics)
        if isinstance(geom, str):
            geom = Registry[f'geom_{geom}']
        elif not (isinstance(geom, type) and
                  issubclass(geom, geom_base_class)):
            raise PlotnineError(
                "geom must either be a geom.geom() "
                "descendant (e.g. plotnine.geom_point), or "
                "a string naming a geom (e.g. 'point', 'text', "
                f"...). Got {repr(geom)}"
            )

        mappings = aes(**{ae: ae for ae in data.columns})

        # The positions are mapped, the rest are manual settings
        self._annotation_geom = geom(
            data,
            mappings,
            stat='identity',
            inherit_aes=False,
            show_legend=False,
            **kwargs
        )

    def __radd__(self, gg, inplace=False):
        gg = gg if inplace else deepcopy(gg)
        gg += self.to_layer()  # Add layer
        return gg

    def to_layer(self):
        """
        Make a layer that represents this annotation

        Returns
        -------
        out : layer
            Layer
        """
        return self._annotation_geom.to_layer()

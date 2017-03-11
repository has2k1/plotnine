from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pandas as pd
import six

from ..aes import aes
from ..utils import is_scalar_or_string, Registry
from ..exceptions import PlotnineError


class annotate(object):
    """
    Create an annotation layer

    Parameters
    ----------
    geom : geom
        Name of geom to use for annotation
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
    kwargs : dict
        Other aesthetics

    Note
    ----
    The positioning aethetics `x`, `y`, `xmin`, `ymin`, `xmax`,
    `ymax`, `xend` and `yend` depend on which `geom` is used.
    You need to choose or ignore accordingly.

    All `geoms` are created with :code:`stat='identity'`.
    """

    def __init__(self, geom, x=None, y=None,
                 xmin=None, xmax=None, xend=None,
                 ymin=None, ymax=None, yend=None,
                 **kwargs):
        variables = locals()

        # position only, and combined aesthetics
        position = {loc: variables[loc]
                    for loc in ('x', 'y',
                                'xmin', 'xmax', 'xend',
                                'ymin', 'ymax', 'yend')
                    if variables[loc] is not None}
        aesthetics = position.copy()
        aesthetics.update(kwargs)

        # Check if the aesthetics are of compatible lengths
        lengths, info_tokens = [], []
        for ae, val in six.iteritems(aesthetics):
            if is_scalar_or_string(val):
                continue
            lengths.append(len(val))
            info_tokens.append((ae, len(val)))

        if len(set(lengths)) > 1:
            details = ', '.join(['{} ({})'.format(n, l)
                                 for n, l in info_tokens])
            msg = 'Unequal parameter lengths: {}'.format(details)
            raise PlotnineError(msg)

        # Stop pandas from complaining about all scalars
        if all(is_scalar_or_string(val) for val in position.values()):
            for ae in position.keys():
                position[ae] = [position[ae]]
                break

        data = pd.DataFrame(position)
        geom = Registry['geom_{}'.format(geom)]
        mappings = aes(**{ae: ae for ae in data.columns})

        # The positions are mapped, the rest are manual settings
        self._annotation_geom = geom(mappings,
                                     data=data,
                                     stat='identity',
                                     inherit_aes=False,
                                     show_legend=False,
                                     **kwargs)

    def __radd__(self, gg, inplace=False):
        return self._annotation_geom.__radd__(gg, inplace=inplace)

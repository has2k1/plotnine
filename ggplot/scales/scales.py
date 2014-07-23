from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import sys
import textwrap

import numpy as np

import ggplot.scales  # TODO: make relative
from ..utils import waiver, identity


def scales_add_defaults(scales, data, aesthetics):
    """
    Add default scales for the aesthetics if none are
    present
    """
    new_scales = []
    if not aesthetics:
        return

    # aesthetics with scales
    if scales:
        aws = reduce(set.union, map(set, [sc.aesthetics for sc in scales]))
    else:
        aws = set()

    # aesthetics that do not have scales present
    new_aesthetics = set(aesthetics.keys()) - aws
    if not new_aesthetics:
        return

    ae_cols = [(ae, aesthetics[ae]) for ae in new_aesthetics
                 if aesthetics[ae] in data.columns]
    for ae, col in ae_cols:
        _type = scale_type(data.loc[:, col])
        scale_name = 'scale_{}_{}'.format(ae, _type)

        try:
            scale_f = getattr(ggplot.scales, scale_name)
        except AttributeError:
            # Skip aesthetics with no scales (e.g. group, order, etc)
            continue
        scales.append(scale_f())


def scale_type(column):
    if column.dtype in (np.number, np.dtype('int64')):
        stype = 'continuous'
    elif column.dtype in (np.dtype('O'), np.bool): # TODO: Add categorical
        stype = 'discrete'
    elif column.dtype == np.dtype('<M8[ns]'):
        stype = 'datetime'
    else:
        msg = """\
            Don't know how to automatically pick scale for \
            object of type {} .Defaulting to 'continuous'""".format(
                column.dtype),
        sys.stderr.write(textwrap.dedent(msg))
        stype = 'continuous'
    return stype

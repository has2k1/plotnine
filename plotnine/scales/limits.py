from contextlib import suppress
from copy import deepcopy
import sys

import pandas as pd

from ..aes import aes, all_aesthetics
from ..geoms import geom_blank
from ..scales.scales import make_scale
from ..exceptions import PlotnineError
from ..utils import array_kind


# By adding limits, we create a scale of the appropriate type

class _lim:
    aesthetic = None

    def __init__(self, *limits):
        if not limits:
            msg = '{}lim(), is missing limits'
            raise PlotnineError(msg.format(self.aesthetic))
        elif len(limits) == 1:
            limits = limits[0]

        series = pd.Series(limits)

        # Type of transform
        if not any(x is None for x in limits) and limits[0] > limits[1]:
            self.trans = 'reverse'
        elif array_kind.continuous(series):
            self.trans = 'identity'
        elif array_kind.discrete(series):
            self.trans = None
        elif array_kind.datetime(series):
            self.trans = 'datetime'
        elif array_kind.timedelta(series):
            self.trans = 'timedelta'
        else:
            msg = 'Unknown type {} of limits'.format(type(limits[0]))
            raise TypeError(msg)

        self.limits = limits
        self.limits_series = series

    def get_scale(self, gg):
        """
        Create a scale
        """
        # This method does some introspection to save users from
        # scale mismatch error. This could happen when the
        # aesthetic is mapped to a categorical but the limits
        # are not provided in categorical form. We only handle
        # the case where the mapping uses an expression to
        # conver to categorical e.g `aes(color='factor(cyl)')`.
        # However if `'cyl'` column is a categorical and the
        # mapping is `aes(color='cyl')`, that will result in
        # an error. If later case proves common enough then we
        # could inspect the data and be clever based on that too!!
        ae = self.aesthetic
        series = self.limits_series
        ae_values = []

        # Look through all the mappings for this aesthetic,
        # if we detect any factor stuff then we convert the
        # limits data to categorical so that the right scale
        # can be choosen. This should take care of the most
        # common use cases.
        for layer in gg.layers:
            with suppress(KeyError):
                value = layer.mapping[ae]
                if isinstance(value, str):
                    ae_values.append(value)

        for value in ae_values:
            if ('factor(' in value or
                    'Categorical(' in value):
                series = pd.Categorical(self.limits_series)
                break
        return make_scale(self.aesthetic,
                          series,
                          limits=self.limits,
                          trans=self.trans)

    def __radd__(self, gg, inplace=False):
        gg = gg if inplace else deepcopy(gg)
        scale = self.get_scale(gg)
        gg.scales.append(scale)
        return gg


class xlim(_lim):
    """
    Set x-axis limits

    Parameters
    ----------
    limits : array_like
        Min and max limits. Must be of size 2.
        You can also pass two values e.g
        ``xlim(40, 100)``
    """
    aesthetic = 'x'


class ylim(_lim):
    """
    Set y-axis limits

    Parameters
    ----------
    limits : array_like
        Min and max limits. Must be of size 2.
        You can also pass two values e.g
        ``ylim(40, 100)``

    Notes
    -----
    If the 2nd value of ``limits`` is less than
    the first, a reversed scale will be created.
    """
    aesthetic = 'y'


class alphalim(_lim):
    aesthetic = 'alpha'


class colorlim(_lim):
    aesthetic = 'color'


class filllim(_lim):
    aesthetic = 'fill'


class linetypelim(_lim):
    aesthetic = 'linetype'


class shapelim(_lim):
    aesthetic = 'shape'


class sizelim(_lim):
    aesthetic = 'size'


class strokelim(_lim):
    aesthetic = 'stroke'


class lims:
    """
    Set aesthtic limits

    Parameters
    ----------
    kwargs : dict
        Aesthetic and the values of the limits.
        e.g ``x=(40, 100)``

    Notes
    -----
    If the 2nd value of ``limits`` is less than
    the first, a reversed scale will be created.
    """

    def __init__(self, **kwargs):
        self._kwargs = kwargs

    def __radd__(self, gg, inplace=False):
        thismodule = sys.modules[__name__]
        for ae, value in self._kwargs.items():
            try:
                klass = getattr(thismodule, '{}lim'.format(ae))
            except AttributeError:
                raise PlotnineError("Cannot change limits for '{}'")

            if inplace:
                gg += klass(value)
            else:
                gg = gg + klass(value)

        return gg


def expand_limits(**kwargs):
    """
    Expand the limits any aesthetic using data

    Parameters
    ----------
    kwargs : dict or dataframe
        Data to use in expanding the limits.
        The keys should be aesthetic names
        e.g. *x*, *y*, *colour*, ...
    """
    def as_list(key):
        with suppress(KeyError):
            if isinstance(kwargs[key], (int, float, str)):
                kwargs[key] = [kwargs[key]]

    if isinstance(kwargs, dict):
        as_list('x')
        as_list('y')
        data = pd.DataFrame(kwargs)
    else:
        data = kwargs

    mapping = aes()
    for ae in set(kwargs) & all_aesthetics:
        mapping[ae] = ae

    return geom_blank(mapping=mapping, data=data, inherit_aes=False)

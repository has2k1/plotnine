import sys
from contextlib import suppress

import pandas as pd

from .._utils import array_kind
from ..exceptions import PlotnineError
from ..geoms import geom_blank
from ..mapping.aes import ALL_AESTHETICS, aes
from ..scales.scales import make_scale


# By adding limits, we create a scale of the appropriate type
class _lim:
    aesthetic = None

    def __init__(self, *limits):
        if not limits:
            msg = "{}lim(), is missing limits"
            raise PlotnineError(msg.format(self.aesthetic))
        elif len(limits) == 1:
            limits = limits[0]

        series = pd.Series(limits)

        # Type of transform
        if not any(x is None for x in limits) and limits[0] > limits[1]:
            self.trans = "reverse"
        elif array_kind.continuous(series):
            self.trans = "identity"
        elif array_kind.discrete(series):
            self.trans = None
        elif array_kind.datetime(series):
            self.trans = "datetime"
        elif array_kind.timedelta(series):
            self.trans = "timedelta"
        else:
            msg = f"Unknown type {type(limits[0])} of limits"
            raise TypeError(msg)

        self.limits = limits
        self.limits_series = series

    def get_scale(self, plot):
        """
        Create a scale
        """
        # This method does some introspection to save users from
        # scale mismatch error. This could happen when the
        # aesthetic is mapped to a categorical but the limits
        # are not provided in categorical form. We only handle
        # the case where the mapping uses an expression to
        # convert to categorical e.g `aes(color="factor(cyl)")`.
        # However if `"cyl"` column is a categorical and the
        # mapping is `aes(color="cyl")`, that will result in
        # an error. If later case proves common enough then we
        # could inspect the data and be clever based on that too!!
        ae = self.aesthetic
        series = self.limits_series
        ae_values = []

        # Look through all the mappings for this aesthetic,
        # if we detect any factor stuff then we convert the
        # limits data to categorical so that the right scale
        # can be chosen. This should take care of the most
        # common use cases.
        for layer in plot.layers:
            with suppress(KeyError):
                value = layer.mapping[ae]
                if isinstance(value, str):
                    ae_values.append(value)

        for value in ae_values:
            if "factor(" in value or "Categorical(" in value:
                series = pd.Categorical(self.limits_series)
                break
        return make_scale(
            self.aesthetic, series, limits=self.limits, trans=self.trans
        )

    def __radd__(self, plot):
        scale = self.get_scale(plot)
        plot.scales.append(scale)
        return plot


class xlim(_lim):
    """
    Set x-axis limits

    Parameters
    ----------
    *limits :
        Min and max limits. Must be of size 2.
        You can also pass two values e.g
        `xlim(40, 100)`
    """

    aesthetic = "x"


class ylim(_lim):
    """
    Set y-axis limits

    Parameters
    ----------
    *limits :
        Min and max limits. Must be of size 2.
        You can also pass two values e.g
        `ylim(40, 100)`

    Notes
    -----
    If the 2nd value of `limits` is less than
    the first, a reversed scale will be created.
    """

    aesthetic = "y"


class alphalim(_lim):
    """
    Alpha limits
    """

    aesthetic = "alpha"


class colorlim(_lim):
    """
    Color limits
    """

    aesthetic = "color"


class filllim(_lim):
    """
    Fill limits
    """

    aesthetic = "fill"


class linetypelim(_lim):
    """
    Linetype limits
    """

    aesthetic = "linetype"


class shapelim(_lim):
    """
    Shapee limits
    """

    aesthetic = "shape"


class sizelim(_lim):
    """
    Size limits
    """

    aesthetic = "size"


class strokelim(_lim):
    """
    Stroke limits
    """

    aesthetic = "stroke"


class lims:
    """
    Set aesthetic limits

    Parameters
    ----------
    kwargs :
        Aesthetic and the values of the limits.
        e.g `x=(40, 100)`

    Notes
    -----
    If the 2nd value of `limits` is less than
    the first, a reversed scale will be created.
    """

    def __init__(self, **kwargs):
        self._kwargs = kwargs

    def __radd__(self, plot):
        """
        Add limits to ggplot object
        """
        thismodule = sys.modules[__name__]
        for ae, value in self._kwargs.items():
            try:
                klass = getattr(thismodule, f"{ae}lim")
            except AttributeError as e:
                msg = "Cannot change limits for '{}'"
                raise PlotnineError(msg) from e

            plot += klass(value)

        return plot


def expand_limits(**kwargs):
    """
    Expand the limits any aesthetic using data

    Parameters
    ----------
    kwargs : dict | dataframe
        Data to use in expanding the limits.
        The keys should be aesthetic names
        e.g. *x*, *y*, *colour*, ...
    """

    def as_list(key):
        with suppress(KeyError):
            if isinstance(kwargs[key], (int, float, str)):
                kwargs[key] = [kwargs[key]]

    if isinstance(kwargs, dict):
        as_list("x")
        as_list("y")
        data = pd.DataFrame(kwargs)
    else:
        data = kwargs

    mapping = aes()
    for ae in set(kwargs) & ALL_AESTHETICS:
        mapping[ae] = ae

    return geom_blank(data=data, mapping=mapping, inherit_aes=False)

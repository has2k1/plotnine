from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from copy import deepcopy
import sys

import pandas as pd
import six

from ..scales.scales import make_scale
from ..utils.exceptions import GgplotError
from ..utils import suppress


# By adding limits, we create a scale of the appropriate type

class _lim(object):
    aesthetic = None

    def __init__(self, *limits):
        if not limits:
            msg = '{}lim(), is missing limits'
            raise GgplotError(msg.format(self.aesthetic))
        elif len(limits) == 1:
            limits = limits[0]

        if limits[0] > limits[1]:
            self.trans = 'reverse'
        else:
            self.trans = 'identity'

        self.limits = limits

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
        series = pd.Series(self.limits)
        ae_values = []

        # Look through all the mappings for this aesthetic,
        # if we detect any factor stuff then we convert the
        # limits data to categorical so that the right scale
        # can be choosen. This should take care of the most
        # common use cases.
        for layer in gg.layers:
            with suppress(KeyError):
                value = layer.mapping[ae]
                if isinstance(value, six.string_types):
                        ae_values.append(value)

        for value in ae_values:
            if ('factor(' in value or
                    'Categorical(' in value):
                series = pd.Categorical(series)
                break
        return make_scale(self.aesthetic,
                          series,
                          limits=self.limits,
                          trans=self.trans)

    def __radd__(self, gg):
        gg = deepcopy(gg)
        scale = self.get_scale(gg)
        gg.scales.append(scale)
        return gg


class xlim(_lim):
    aesthetic = 'x'


class ylim(_lim):
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


class lims(object):

    def __init__(self, **kwargs):
        self._kwargs = kwargs

    def __radd__(self, gg):
        thismodule = sys.modules[__name__]
        for ae, value in self._kwargs.items():
            try:
                klass = getattr(thismodule, '{}lim'.format(ae))
            except AttributeError:
                raise GgplotError("Cannot change limits for '{}'")
            gg = gg + klass(value)

        return gg

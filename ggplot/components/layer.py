from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import six
from copy import deepcopy

import numpy as np
import pandas as pd
import matplotlib.cbook as cbook
import pandas.core.common as com
from patsy.eval import EvalEnvironment

from ..scales.scales import scales_add_defaults
from ..utils.exceptions import GgplotError
from ..utils import DISCRETE_KINDS, ninteraction
from ..utils import check_required_aesthetics, defaults
from ..utils import is_string, gg_import, suppress
from ..positions.position import position
from .aes import aes, is_calculated_aes, strip_dots

_TPL_EVAL_FAIL = """\
Could not evaluate the '{}' mapping: '{}' \
(original error: {})"""

_TPL_BAD_EVAL_TYPE = """\
The '{}' mapping: '{}' produced a value of type '{}',\
but only single items and lists/arrays can be used. \
(original error: {})"""


class Layers(list):
    """
    List of layers

    Each layer knows its position/zorder (1 based) in the list.
    """

    def append(self, item):
        item.zorder = len(self) + 1
        return list.append(self, item)

    def _set_zorder(self, lst2):
        base = len(self)
        for i, item in enumerate(lst2):
            item.zorder = base + 1
        return lst2

    def extend(self, other):
        other = self._set_zorder(other)
        return list.extend(self, other)

    def __iadd__(self, other):
        other = self._set_zorder(other)
        return list.__iadd__(self, other)

    def __add__(self, other):
        other = self._set_zorder(other)
        return list.__add__(self, other)


class layer(object):

    def __init__(self, geom=None, stat=None,
                 data=None, mapping=None,
                 position=None, inherit_aes=True,
                 show_guide=None):
        self.geom = geom
        self.stat = stat
        self.data = data
        self.mapping = mapping
        self.position = self._position_object(position)
        self.inherit_aes = inherit_aes
        self.show_guide = show_guide
        self._active_mapping = {}
        self.zorder = 0

    def __deepcopy__(self, memo):
        """
        Deep copy without copying the self.data dataframe
        """
        # In case the object cannot be initialized with out
        # arguments
        class _empty(object):
            pass
        result = _empty()
        result.__class__ = self.__class__
        for key, item in self.__dict__.items():
            # don't make a deepcopy of data!
            if key == "data":
                result.__dict__[key] = self.__dict__[key]
                continue
            result.__dict__[key] = deepcopy(self.__dict__[key], memo)
        return result

    def _position_object(self, name):
        """
        Return an instantiated position object
        """
        if issubclass(type(name), position):
            return name

        if not is_string(name):
            raise GgplotError(
                'Unknown position of type {}'.format(type(name)))

        if not name.startswith('position_'):
            name = 'position_{}'.format(name)

        return gg_import(name)()

    def layer_mapping(self, mapping):
        """
        Return the mappings that are active in this layer

        Parameters
        ----------
        mapping : aes
            mappings in the ggplot call

        Note
        ----
        Once computed the layer mappings are also stored
        in self._active_mapping
        """
        # For certain geoms, it is useful to be able to
        # ignore the default aesthetics and only use those
        # set in the layer
        if self.inherit_aes:
            aesthetics = defaults(self.mapping, mapping)
        else:
            aesthetics = self.mapping

        # drop aesthetic parameters or the calculated aesthetics
        calculated = set(is_calculated_aes(aesthetics))
        d = dict((ae, v) for ae, v in aesthetics.items()
                 if (ae not in self.geom.aes_params) and
                 (ae not in calculated))
        self._active_mapping = aes(**d)
        return self._active_mapping

    def compute_aesthetics(self, data, plot):
        """
        Return a dataframe where the columns match the
        aesthetic mappings.

        Transformations like 'factor(cyl)' and other
        expression evaluation are  made in here
        """
        aesthetics = self.layer_mapping(plot.mapping)

        # Override grouping if set in layer.
        with suppress(KeyError):
            aesthetics['group'] = self.geom.aes_params['group']

        env = EvalEnvironment.capture(eval_env=plot.plot_env)
        env = env.with_outer_namespace({'factor': pd.Categorical})

        evaled = pd.DataFrame(index=data.index)
        has_aes_params = False  # aesthetic parameter in aes()

        # If a column name is not in the data, it is evaluated/transformed
        # in the environment of the call to ggplot
        for ae, col in aesthetics.items():
            if isinstance(col, six.string_types):
                if col in data:
                    evaled[ae] = data[col]
                else:
                    try:
                        new_val = env.eval(col, inner_namespace=data)
                    except Exception as e:
                        raise GgplotError(
                            _TPL_EVAL_FAIL.format(ae, col, str(e)))

                    try:
                        evaled[ae] = new_val
                    except Exception as e:
                        raise GgplotError(
                            _TPL_BAD_EVAL_TYPE.format(
                                ae, col, str(type(new_val)), str(e)))
            elif com.is_list_like(col):
                n = len(col)
                if n != len(data) and n != 1:
                    raise GgplotError(
                        "Aesthetics must either be length one, " +
                        "or the same length as the data")
                elif n == 1:
                    col = col[0]
                has_aes_params = True
                evaled[ae] = col
            elif not cbook.iterable(col) and cbook.is_numlike(col):
                evaled[ae] = col
            else:
                msg = "Do not know how to deal with aesthetic '{}'"
                raise GgplotError(msg.format(ae))

        # int columns are continuous, cast them to floats.
        # Also when categoricals are mapped onto scales,
        # they create int columns.
        # Some stats e.g stat_bin need this distinction
        for col in evaled:
            if evaled[col].dtype == np.int:
                evaled[col] = evaled[col].astype(np.float)

        evaled_aes = aes(**dict((col, col) for col in evaled))
        scales_add_defaults(plot.scales, evaled, evaled_aes)

        if len(data) == 0 and has_aes_params:
            # No data, and vectors suppled to aesthetics
            evaled['PANEL'] = 1
        else:
            evaled['PANEL'] = data['PANEL']

        evaled = add_group(evaled)
        return evaled

    def compute_statistic(self, data, panel):
        """
        Compute & return statistics for this layer
        """
        if not len(data):
            return pd.DataFrame()

        params = self.stat.setup_params(data)
        return self.stat.compute_layer(data, params, panel)

    def map_statistic(self, data, plot):
        """
        Mapping aesthetics to computed statistics
        """
        if len(data) == 0:
            return pd.DataFrame()

        # Assemble aesthetics from layer, plot and stat mappings
        aesthetics = deepcopy(self.mapping)
        if self.inherit_aes:
            aesthetics = defaults(aesthetics, plot.mapping)

        aesthetics = defaults(aesthetics, self.stat.DEFAULT_AES)

        # The new aesthetics are those that the stat calculates
        # and have been mapped to with dot dot notation
        # e.g aes(y='..count..'), y is the new aesthetic and
        # 'count' is the computed column in data
        new = {}  # {'aesthetic_name': 'calculated_stat'}
        stat_data = pd.DataFrame()
        for ae in is_calculated_aes(aesthetics):
            new[ae] = strip_dots(aesthetics[ae])
            # In conjuction with the pd.concat at the end,
            # be careful not to create duplicate columns
            # for cases like y='..y..'
            if ae != new[ae]:
                stat_data[ae] = data[new[ae]]

        if not new:
            return data

        # Add any new scales, if needed
        scales_add_defaults(plot.scales, data, new)

        # Transform the values, if the scale say it's ok
        # (see stat_spoke for one exception)
        if self.stat.retransform:
            stat_data = plot.scales.transform_df(stat_data)

        data = pd.concat([data, stat_data], axis=1)
        return data

    def setup_data(self, data):
        """
        Prepare/modify data for plotting
        """
        if len(data) == 0:
            return pd.DataFrame()

        data = self.geom.setup_data(data)

        check_required_aesthetics(
            self.geom.REQUIRED_AES,
            set(data.columns) | set(self.geom.aes_params),
            self.geom.__class__.__name__)
        return data

    def compute_position(self, data, panel):
        """
        Compute the position of each geometric object
        in concert with the other objects in the panel
        """
        params = self.position.setup_params(data)
        data = self.position.setup_data(data, params)
        return self.position.compute_layer(data, params, panel)

    def draw(self, data, panel, coord):
        """
        Draw geom

        Parameters
        ----------
        data : DataFrame
            DataFrame specific for this layer
        panel : Panel
            Panel object created when the plot is getting
            built
        coord : coord
            Type of coordinate axes
        """
        self.geom.draw_layer(data, panel, coord, self.zorder)

    def use_defaults(self, data):
        """
        Prepare/modify data for plotting
        """
        return self.geom.use_defaults(data)


def add_group(data):
    if len(data) == 0:
        return data
    if not ('group' in data):
        disc = discrete_columns(data, ignore=['label'])
        if disc:
            data['group'] = ninteraction(data[disc], drop=True)
        else:
            data['group'] = 1
    else:
        data['group'] = ninteraction(data[['group']], drop=True)

    return data


def discrete_columns(df, ignore):
    """
    Return a list of the discrete columns in the
    dataframe `df`. `ignore` is a list|set|tuple with the
    names of the columns to skip.
    """
    lst = []
    for col in df:
        if (df[col].dtype.kind in DISCRETE_KINDS) and not (col in ignore):
            lst.append(col)
    return lst

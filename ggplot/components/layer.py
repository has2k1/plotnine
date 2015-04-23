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
from ..utils import discrete_dtypes, ninteraction
from ..utils import check_required_aesthetics, defaults
from ..utils import is_string, gg_import, groupby_apply
from ..utils import is_scalar_or_string
from ..positions.position import _position_base
from .aes import aes, is_calculated_aes, strip_dots, aesdefaults

_TPL_EVAL_FAIL = """\
Could not evaluate the '{}' mapping: '{}' \
(original error: {})"""

_TPL_BAD_EVAL_TYPE = """\
The '{}' mapping: '{}' produced a value of type '{}',\
but only single items and lists/arrays can be used. \
(original error: {})"""


class layer(object):

    def __init__(self, geom=None, stat=None,
                 data=None, mapping=None,
                 position=None, params=None,
                 inherit_aes=True, group=None,
                 show_guide=None):
        self.geom = geom
        self.stat = stat
        self.data = data
        self.mapping = mapping
        self.position = self._position_object(position)
        self.params = params
        self.inherit_aes = inherit_aes
        self.group = group
        self.show_guide = show_guide
        self._active_mapping = {}

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
        if issubclass(type(name), _position_base):
            return name

        if not is_string(name):
            raise GgplotError(
                'Unknown position of type {}'.format(type(name)))

        if not name.startswith('position_'):
            name = 'position_' + name

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

        # drop aesthetics that are manual or calculated
        manual = set(self.geom.manual_aes.keys())
        calculated = set(is_calculated_aes(aesthetics))
        d = dict((ae, v) for ae, v in aesthetics.items()
                 if not (ae in manual) and not (ae in calculated))
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
        if self.group is not None:
            aesthetics['group'] = self.group

        def factor(s):
            return pd.Categorical(s)

        env = EvalEnvironment.capture(eval_env=plot.plot_env)
        env.add_outer_namespace({"factor": factor})

        evaled = pd.DataFrame()
        settings = False  # Indicate manual settings within aes()

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
                settings = True
                evaled[ae] = col
            elif not cbook.iterable(col) and cbook.is_numlike(col):
                evaled[ae] = col
            else:
                msg = "Do not know how to deal with aesthetic '{}'"
                raise GgplotError(msg.format(ae))

        evaled_aes = aes(**dict((col, col) for col in evaled))
        scales_add_defaults(plot.scales, evaled, evaled_aes)

        if len(data) == 0 and settings:
            # No data, and vectors suppled to aesthetics
            evaled['PANEL'] = 1
        else:
            evaled['PANEL'] = data['PANEL']

        return evaled

    def calc_statistic(self, data, scales):
        """
        Verify required aethetics and return the
        statistics as computed by the stat object
        """
        if not len(data):
            return pd.DataFrame()

        check_required_aesthetics(
            self.stat.REQUIRED_AES,
            list(data.columns) + list(self.stat.params.keys()),
            self.stat.__class__.__name__)

        return self.stat._calculate_groups(data, scales)

    def map_statistic(self, data, plot):
        """
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

    def reparameterise(self, data):
        if len(data) == 0:
            return pd.DataFrame()
        return self.geom.reparameterise(data)

    def adjust_position(self, data):
        """
        Adjust the position of each geometric object
        in concert with the other objects in the panel
        """
        data = groupby_apply(data, 'PANEL', self.position.adjust)
        return data

    def draw(self, data, scales, ax, zorder):
        """
        Draw layer

        Parameters
        ----------
        data : DataFrame
            DataFrame specific for this layer
        scales : dict
            Has two keys, 'x' and 'y' whose values
            are the x and y scales respectively
        ax : axes
            On which to draw the layer
        zorder : int
            Stacking order of the layer in the plot
        """
        check_required_aesthetics(
            self.geom.REQUIRED_AES,
            set(data.columns) | set(self.geom.manual_aes),
            self.geom.__class__.__name__)

        kwargs = deepcopy(self.geom.params)
        kwargs['zorder'] = zorder
        self.geom.draw_groups(data, scales, ax, **kwargs)

    def use_defaults(self, data):
        """
        Return dataframe with aesthetic parameter setting and
        default aesthetic values. i.e. Unmapped aesthetics
        and their values
        """
        df = aesdefaults(data, self.geom.DEFAULT_AES, None)

        # Override mappings with atomic parameters
        gp = ((set(df.columns) | set(self.geom.REQUIRED_AES)) &
              set(self.geom.manual_aes))
        for ae in self.geom.manual_aes:
            if not is_scalar_or_string(self.geom.manual_aes[ae]):
                try:
                    gp.remove(ae)
                except KeyError:
                    pass

        gp = list(gp)

        # Check that mappings are compatable length: either 1 or
        # the same length
        def llen(var):
            if is_scalar_or_string(var):
                return 1
            return len(var)

        param_lengths = np.array(
            [llen(self.geom.manual_aes[ae]) for ae in gp])

        bad = (param_lengths != 1) & (param_lengths != len(df))
        if any(bad):
            msg = "Incompatible lengths for set aesthetics: {}"
            raise GgplotError(msg.format(', '.join(df[bad].columns)))

        for ae in gp:
            df[ae] = self.geom.manual_aes[ae]

        return df


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
        if (df[col].dtype in discrete_dtypes) and not (col in ignore):
            lst.append(col)
    return lst

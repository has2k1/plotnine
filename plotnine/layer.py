from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import six
from copy import copy, deepcopy

import pandas as pd
import matplotlib.cbook as cbook
import pandas.api.types as pdtypes
from patsy.eval import EvalEnvironment

from .exceptions import PlotnineError
from .utils import array_kind, ninteraction, suppress
from .utils import check_required_aesthetics, defaults
from .aes import aes, is_calculated_aes, strip_dots, make_labels

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

    During the plot building pipeline, many operations are
    applied at all layers in the plot. This class makes those
    tasks easier.
    """

    def __iadd__(self, other):
        return Layers(super(Layers, self).__iadd__(other))

    def __add__(self, other):
        return Layers(super(Layers, self).__add__(other))

    def __radd__(self, other, inplace=False):
        """
        Add layers to ggplot object
        """
        from .ggplot import ggplot
        if isinstance(other, ggplot):
            other = other if inplace else deepcopy(other)
            for obj in self:
                other += obj
        else:
            msg = "Cannot add Layers to object of type {!r}".format
            raise PlotnineError(msg(type(other)))
        return other

    def __getitem__(self, key):
        result = super(Layers, self).__getitem__(key)
        if not isinstance(key, int):
            result = Layers(result)
        return result

    @property
    def data(self):
        return [l.data for l in self]

    def generate_data(self, plot_data):
        for l in self:
            l.generate_data(plot_data)

    def setup_data(self):
        for l in self:
            l.setup_data()

    def draw(self, layout, coord):
        # If zorder is 0, it is left to MPL
        for i, l in enumerate(self, start=1):
            l.zorder = i
            l.draw(layout, coord)

    def compute_aesthetics(self, plot):
        for l in self:
            l.compute_aesthetics(plot)

    def compute_statistic(self, layout):
        for l in self:
            l.compute_statistic(layout)

    def map_statistic(self, plot):
        for l in self:
            l.map_statistic(plot)

    def compute_position(self, layout):
        for l in self:
            l.compute_position(layout)

    def use_defaults(self):
        for l in self:
            l.use_defaults()

    def transform(self, scales):
        for l in self:
            l.data = scales.transform_df(l.data)

    def train(self, scales):
        for l in self:
            l.data = scales.train_df(l.data)

    def map(self, scales):
        for l in self:
            l.data = scales.map_df(l.data)

    def finish_statistics(self):
        for l in self:
            l.finish_statistics()


class layer(object):
    """
    Layer

    When a ``geom`` or ``stat`` is added to a
    :class:`~plotnine.ggplot` object, it creates a single layer.
    This class is a representation of that layer.

    Parameters
    ----------
    geom : geom, optional
        geom to used to draw this layer.
    stat : stat, optional
        stat used for the statistical transformation of
        data in this layer
    data : pandas.DataFrame, optional
        Data plotted in this layer. If ``None``, the data from
        the :class:`~plotnine.ggplot` object will be used.
    mapping : aes, optional
        Aesthetic mappings.
    position : position, optional
        Position object to adjust the geometries in this layer.
    inherit_aes : bool, optional
        If ``True`` inherit from the aesthetic mappings of
        the :class:`~plotnine.ggplot` object. Default ``True``.
    show_legend : bool or None, optional
        Whether to make up and show a legend for the mappings
        of this layer. If ``None`` then an automatic/good choice
        is made. Default is ``None``.

    Note
    ----
    There is no benefit to manually creating a layer. You should
    always use a ``geom`` or ``stat``.
    """

    def __init__(self, geom=None, stat=None, data=None, mapping=None,
                 position=None, inherit_aes=True, show_legend=None):
        self.geom = geom
        self.stat = stat
        self.data = data
        self.mapping = mapping
        self.position = position
        self.inherit_aes = inherit_aes
        self.show_legend = show_legend
        self._active_mapping = {}
        self.zorder = 0

    @staticmethod
    def from_geom(geom):
        """
        Create a layer given a :class:`geom`

        Parameters
        ----------
        geom : geom
            `geom` from which a layer will be created

        Returns
        -------
        out : layer
            Layer that represents the specific `geom`.
        """
        kwargs = geom._kwargs
        lkwargs = {'geom': geom,
                   'mapping': geom.mapping,
                   'data': geom.data,
                   'stat': geom._stat,
                   'position': geom._position}

        for param in ('show_legend', 'inherit_aes'):
            if param in kwargs:
                lkwargs[param] = kwargs[param]
            elif param in geom.DEFAULT_PARAMS:
                lkwargs[param] = geom.DEFAULT_PARAMS[param]

        return layer(**lkwargs)

    def __radd__(self, gg):
        """
        Add layer to ggplot object
        """
        try:
            gg.layers.append(self)
        except AttributeError:
            msg = "Cannot add layer to object of type {!r}".format
            raise PlotnineError(msg(type(gg)))

        # Add any new labels
        mapping = make_labels(self.mapping)
        default = make_labels(self.stat.DEFAULT_AES)
        new_labels = defaults(mapping, default)
        gg.labels = defaults(gg.labels, new_labels)
        return gg

    def __deepcopy__(self, memo):
        """
        Deep copy without copying the self.data dataframe
        """
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        old = self.__dict__
        new = result.__dict__

        for key, item in old.items():
            if key == 'data':
                new[key] = old[key]
            else:
                new[key] = deepcopy(old[key], memo)

        return result

    def generate_data(self, plot_data):
        """
        Generate data to be used by this layer

        Parameters
        ----------
        plot_data : dataframe
            ggplot object data
        """
        # Each layer that does not have data gets a copy of
        # of the ggplot.data. If the has data it is replaced
        # by copy so that we do not alter the users data
        if self.data is None:
            self.data = plot_data.copy()
        elif hasattr(self.data, '__call__'):
            self.data = self.data(plot_data)
            if not isinstance(self.data, pd.DataFrame):
                raise PlotnineError(
                    "Data function must return a dataframe")
        else:
            self.data = self.data.copy()

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

    def compute_aesthetics(self, plot):
        """
        Return a dataframe where the columns match the
        aesthetic mappings.

        Transformations like 'factor(cyl)' and other
        expression evaluation are  made in here
        """
        data = self.data
        aesthetics = self.layer_mapping(plot.mapping)

        # Override grouping if set in layer.
        with suppress(KeyError):
            aesthetics['group'] = self.geom.aes_params['group']

        env = EvalEnvironment.capture(eval_env=plot.environment)
        env = env.with_outer_namespace({'factor': pd.Categorical})

        # Using `type` preserves the subclass of pd.DataFrame
        evaled = type(data)(index=data.index)

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
                        raise PlotnineError(
                            _TPL_EVAL_FAIL.format(ae, col, str(e)))

                    try:
                        evaled[ae] = new_val
                    except Exception as e:
                        raise PlotnineError(
                            _TPL_BAD_EVAL_TYPE.format(
                                ae, col, str(type(new_val)), str(e)))
            elif pdtypes.is_list_like(col):
                n = len(col)
                if len(data) and n != len(data) and n != 1:
                    raise PlotnineError(
                        "Aesthetics must either be length one, " +
                        "or the same length as the data")
                # An empty dataframe does not admit a scalar value
                elif len(evaled) and n == 1:
                    col = col[0]
                evaled[ae] = col
            elif not cbook.iterable(col) and cbook.is_numlike(col):
                # An empty dataframe does not admit a scalar value
                if not len(evaled):
                    col = [col]
                evaled[ae] = col
            else:
                msg = "Do not know how to deal with aesthetic '{}'"
                raise PlotnineError(msg.format(ae))

        evaled_aes = aes(**dict((col, col) for col in evaled))
        plot.scales.add_defaults(evaled, evaled_aes)

        if len(data) == 0 and len(evaled) > 0:
            # No data, and vectors suppled to aesthetics
            evaled['PANEL'] = 1
        else:
            evaled['PANEL'] = data['PANEL']

        self.data = add_group(evaled)

    def compute_statistic(self, layout):
        """
        Compute & return statistics for this layer
        """
        data = self.data
        if not len(data):
            return type(data)()

        params = self.stat.setup_params(data)
        data = self.stat.use_defaults(data)
        data = self.stat.setup_data(data)
        data = self.stat.compute_layer(data, params, layout)
        self.data = data

    def map_statistic(self, plot):
        """
        Mapping aesthetics to computed statistics
        """
        data = self.data
        if not len(data):
            return type(data)()

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
        stat_data = type(data)()
        for ae in is_calculated_aes(aesthetics):
            new[ae] = strip_dots(aesthetics[ae])
            # In conjuction with the pd.concat at the end,
            # be careful not to create duplicate columns
            # for cases like y='..y..'
            if new[ae] != ae:
                stat_data[ae] = plot.environment.eval(
                    new[ae], inner_namespace=data)

        if not new:
            return

        # (see stat_spoke for one exception)
        if self.stat.retransform:
            stat_data = plot.scales.transform_df(stat_data)

        self.data = pd.concat([data, stat_data], axis=1)

        # Add any new scales, if needed
        plot.scales.add_defaults(self.data, new)

    def setup_data(self):
        """
        Prepare/modify data for plotting
        """
        data = self.data
        if len(data) == 0:
            return type(data)()

        data = self.geom.setup_data(data)

        check_required_aesthetics(
            self.geom.REQUIRED_AES,
            set(data.columns) | set(self.geom.aes_params),
            self.geom.__class__.__name__)

        self.data = data

    def compute_position(self, layout):
        """
        Compute the position of each geometric object
        in concert with the other objects in the panel
        """
        params = self.position.setup_params(self.data)
        data = self.position.setup_data(self.data, params)
        data = self.position.compute_layer(data, params, layout)
        self.data = data

    def draw(self, layout, coord):
        """
        Draw geom

        Parameters
        ----------
        layout : Layout
            Layout object created when the plot is getting
            built
        coord : coord
            Type of coordinate axes
        """
        params = copy(self.geom.params)
        params.update(self.stat.params)
        params['zorder'] = self.zorder
        self.data = self.geom.handle_na(self.data)
        # At this point each layer must have the data
        # that is created by the plot build process
        self.geom.draw_layer(self.data, layout, coord, **params)

    def use_defaults(self, data=None):
        """
        Prepare/modify data for plotting
        """
        if data is None:
            data = self.data
        return self.geom.use_defaults(data)

    def finish_statistics(self):
        """
        Prepare/modify data for plotting
        """
        # params = self.stat.setup_params(self.data)
        self.stat.finish_layer(self.data, self.stat.params)


NO_GROUP = -1


def add_group(data):
    if len(data) == 0:
        return data

    if 'group' not in data:
        disc = discrete_columns(data, ignore=['label'])
        if disc:
            data['group'] = ninteraction(data[disc], drop=True)
        else:
            data['group'] = NO_GROUP
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
        if array_kind.discrete(df[col]) and (col not in ignore):
            # Some columns are represented as object dtype
            # but may have compound structures as values.
            try:
                hash(df[col].iloc[0])
            except TypeError:
                continue
            lst.append(col)
    return lst

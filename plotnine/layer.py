from copy import copy, deepcopy

import pandas as pd

from .exceptions import PlotnineError
from .utils import array_kind, ninteraction
from .utils import check_required_aesthetics, defaults
from .mapping.aes import aes, NO_GROUP, SCALED_AESTHETICS
from .mapping.evaluation import stage, evaluate


class Layers(list):
    """
    List of layers

    During the plot building pipeline, many operations are
    applied at all layers in the plot. This class makes those
    tasks easier.
    """

    def __iadd__(self, other):
        return Layers(super().__iadd__(other))

    def __add__(self, other):
        return Layers(super().__add__(other))

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
        result = super().__getitem__(key)
        if not isinstance(key, int):
            result = Layers(result)
        return result

    @property
    def data(self):
        return [l.data for l in self]

    def setup(self, plot):
        for l in self:
            l.setup(plot)

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

    def use_defaults(self, data=None, aes_modifiers=None):
        for l in self:
            l.use_defaults(data, aes_modifiers)

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

    def update_labels(self, plot):
        for l in self:
            plot._update_labels(l)


class layer:
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
    data : dataframe, optional
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
    raster : bool, optional (default: False)
        If ``True``, draw onto this layer a raster (bitmap) object
        even if the final image format is vector.

    Notes
    -----
    There is no benefit to manually creating a layer. You should
    always use a ``geom`` or ``stat``.
    """

    def __init__(self, geom=None, stat=None, data=None, mapping=None,
                 position=None, inherit_aes=True, show_legend=None,
                 raster=False):
        self.geom = geom
        self.stat = stat
        self.data = data
        self.mapping = mapping
        self.position = position
        self.inherit_aes = inherit_aes
        self.show_legend = show_legend
        self.raster = raster
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

        layer_params = ('inherit_aes', 'show_legend', 'raster')
        for param in layer_params:
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

    def setup(self, plot):
        """
        Prepare layer for the plot building

        Give the layer access to the data, mapping and environment
        """
        self._make_layer_data(plot.data)
        self._make_layer_mapping(plot.mapping)
        self._make_layer_environments(plot.environment)

    def _make_layer_data(self, plot_data):
        """
        Generate data to be used by this layer

        Parameters
        ----------
        plot_data : dataframe
            ggplot object data
        """
        if plot_data is None:
            plot_data = pd.DataFrame()

        # Each layer that does not have data gets a copy of
        # of the ggplot.data. If the has data it is replaced
        # by copy so that we do not alter the users data
        if self.data is None:
            try:
                self.data = plot_data.copy()
            except AttributeError:
                _geom_name = self.geom.__class__.__name__
                _data_name = plot_data.__class__.__name__
                raise PlotnineError(
                    f"{_geom_name} layer expects a dataframe, "
                    f"but it got {_data_name} instead."
                )
        elif callable(self.data):
            self.data = self.data(plot_data)
            if not isinstance(self.data, pd.DataFrame):
                raise PlotnineError(
                    "Data function must return a dataframe"
                )
        else:
            self.data = self.data.copy()

    def _make_layer_mapping(self, plot_mapping):
        """
        Create the aesthetic mappings to be used by this layer

        Parameters
        ----------
        plot_mapping : aes
            ggplot object mapping
        """
        if self.inherit_aes:
            self.mapping = defaults(self.mapping, plot_mapping)

        # aesthetics set as parameters override the same
        # aesthetics set as mappings, so we can ignore
        # those in the mapping
        for ae in self.geom.aes_params:
            if ae in self.mapping:
                del self.mapping[ae]

        # Set group as a mapping if set as a parameter
        if 'group' in self.geom.aes_params:
            group = self.geom.aes_params['group']
            # Double quote str so that it evaluates to itself
            if isinstance(group, str):
                group = f'"{group}"'
            self.mapping['group'] = stage(start=group)

    def _make_layer_environments(self, plot_environment):
        """
        Create the aesthetic mappings to be used by this layer

        Parameters
        ----------
        plot_environment : ~patsy.Eval.EvalEnvironment
            Namespace in which to execute aesthetic expressions.
        """
        self.geom.environment = plot_environment
        self.stat.environment = plot_environment

    def compute_aesthetics(self, plot):
        """
        Return a dataframe where the columns match the
        aesthetic mappings.

        Transformations like 'factor(cyl)' and other
        expression evaluation are  made in here
        """
        evaled = evaluate(self.mapping._starting, self.data, plot.environment)
        evaled_aes = aes(**{col: col for col in evaled})
        plot.scales.add_defaults(evaled, evaled_aes)

        if len(self.data) == 0 and len(evaled) > 0:
            # No data, and vectors suppled to aesthetics
            evaled['PANEL'] = 1
        else:
            evaled['PANEL'] = self.data['PANEL']

        data = add_group(evaled)
        self.data = data.sort_values('PANEL', kind='mergesort')

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

        # Mixin default stat aesthetic mappings
        aesthetics = defaults(self.mapping, self.stat.DEFAULT_AES)
        stat_data = evaluate(aesthetics._calculated, data, plot.environment)

        if not len(stat_data):
            return

        # (see stat_spoke for one exception)
        if self.stat.retransform:
            stat_data = plot.scales.transform_df(stat_data)

        # When there are duplicate columns, we use the computed
        # ones in stat_data
        columns = data.columns.difference(stat_data.columns)
        self.data = pd.concat([data[columns], stat_data], axis=1)

        # Add any new scales, if needed
        new = {ae: ae for ae in stat_data.columns}
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
            self.geom.__class__.__name__
        )

        self.data = data

    def compute_position(self, layout):
        """
        Compute the position of each geometric object
        in concert with the other objects in the panel
        """
        if len(self.data) == 0:
            return self.data

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
        params['raster'] = self.raster
        self.data = self.geom.handle_na(self.data)
        # At this point each layer must have the data
        # that is created by the plot build process
        self.geom.draw_layer(self.data, layout, coord, **params)

    def use_defaults(self, data=None, aes_modifiers=None):
        """
        Prepare/modify data for plotting

        Parameters
        ----------
        data : dataframe, optional
            Data
        aes_modifiers : dict
            Expression to evaluate and replace aesthetics in
            the data.
        """
        if data is None:
            data = self.data

        if aes_modifiers is None:
            aes_modifiers = self.mapping._scaled

        return self.geom.use_defaults(data, aes_modifiers)

    def finish_statistics(self):
        """
        Prepare/modify data for plotting
        """
        self.stat.finish_layer(self.data, self.stat.params)


def add_group(data):
    """
    Add group to the dataframe

    The group depends on the interaction of the discrete
    aesthetic columns in the dataframe.
    """
    if len(data) == 0:
        return data

    if 'group' not in data:
        ignore = data.columns.difference(SCALED_AESTHETICS)
        disc = discrete_columns(data, ignore=ignore)
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

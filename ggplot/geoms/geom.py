from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from copy import deepcopy

import pandas as pd

from ..components.aes import aes, make_labels, rename_aesthetics
from ..components.layer import layer
from ..utils.exceptions import GgplotError
from ..utils import gg_import, defaults, suppress, copy_keys
from ..stats.stat import stat


class geom(object):
    """Base class of all Geoms"""
    DEFAULT_AES = dict()
    REQUIRED_AES = set()
    DEFAULT_PARAMS = dict()

    data = None           # geom/layer specific dataframe
    mapping = None        # mappings i.e aes(x=col1, fill=col2, ...)
    aes_params = None     # setting of aesthetic
    params = None         # parameter settings

    # The geom responsible for the legend if draw_legend is
    # not implemented
    legend_geom = 'point'

    # A matplotlib plot function may require that an aethestic have a
    # single unique value. e.g. linestyle='dashed' and not
    # linestyle=['dashed', 'dotted', ...].
    # A single call to such a function can only plot lines with the
    # same linestyle. However, if the plot we want has more than one
    # line with different linestyles, we need to group the lines with
    # the same linestyle and plot them as one unit.
    #
    # geoms should fill out this set with such aesthetics so that the
    # plot information they receive can be plotted in a single call.
    # See: geom_point
    _units = set()

    def __init__(self, *args, **kwargs):
        kwargs = rename_aesthetics(kwargs)
        kwargs = self._sanitize_arguments(args, kwargs)
        self._cache = {'kwargs': kwargs}  # for making stat & layer
        self._stat = self._make_stat()
        self.verify_arguments(kwargs)     # geom, stat, layer

        # separate aesthetics and parameters
        self.aes_params = copy_keys(kwargs, {}, self.aesthetics())
        self.params = copy_keys(kwargs, deepcopy(self.DEFAULT_PARAMS))
        self.mapping = kwargs['mapping']
        self.data = kwargs['data']

    @classmethod
    def aesthetics(cls):
        """
        Return all the aesthetics for this geom
        """
        main = cls.DEFAULT_AES.viewkeys() | cls.REQUIRED_AES
        other = {'group'}
        # Need to recognize both spellings
        if 'color' in main:
            other.add('colour')
        if 'outlier_color' in main:
            other.add('outlier_colour')
        return main | other

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

    def setup_data(self, data):
        return data

    def use_defaults(self, data):
        """
        Combine data with defaults and set aesthetics from parameters
        """
        missing_aes = (self.DEFAULT_AES.viewkeys() -
                       self.aes_params.viewkeys() -
                       set(data.columns))

        # Not in data and not set, use default
        for ae in missing_aes:
            data[ae] = self.DEFAULT_AES[ae]

        # If set, use it
        for ae in self.aes_params:
            data[ae] = self.aes_params[ae]

        return data

    def draw_layer(self, data, panel, coord, zorder):
        """
        Draw layer across all panels

        Parameters
        ----------
        data : DataFrame
            DataFrame specific for this layer
        panel : Panel
            Panel object created when the plot is getting
            built
        coord : coord
            Type of coordinate axes
        zorder : int
            Stacking order of the layer in the plot
        """
        params = deepcopy(self.params)
        params.update(self._stat.params)
        params['zorder'] = zorder
        for pid, pdata in data.groupby('PANEL'):
            pdata.is_copy = None
            ploc = pid - 1
            panel_scales = panel.ranges[ploc]
            ax = panel.axs[ploc]
            self.draw_panel(pdata, panel_scales, coord, ax, **params)

    def draw_panel(self, data, panel_scales, coord, ax, **params):
        """
        Plot all groups

        For effeciency, geoms that do not need to partition
        different groups before plotting should override this
        method and avoid the groupby.

        Parameters
        ----------
        data : dataframe
            Data to be plotted by this geom. This is the
            dataframe created in the plot_build pipeline
        scales : dict
            The scale information as may be required by the
            axes. At this point, that information is about
            ranges, ticks and labels. Keys of interest to
            the geom are:
                - 'x_range' -- tuple
                - 'y_range' -- tuple
        coord : coord
            Coordinate (e.g. coord_cartesian) system of the
            geom
        ax : axes
            Axes on which to plot
        params : dict
            Combined parameters for the geom and stat. Also
            includes the 'zorder'.
        """
        for _, gdata in data.groupby('group'):
            pinfos = self._make_pinfos(gdata, params)
            for pinfo in pinfos:
                self.draw_group(pinfo, panel_scales, coord, ax, **params)

    @staticmethod
    def draw_group(pinfo, panel_scales, coord, ax, **params):
        msg = "The geom should implement this method."
        raise NotImplementedError(msg)

    def __radd__(self, gg):
        gg = deepcopy(gg)

        # create and add layer
        gg.layers.append(self._make_layer())

        # Add any new labels
        mapping = make_labels(self.mapping)
        default = make_labels(self._stat.DEFAULT_AES)
        new_labels = defaults(mapping, default)
        gg.labels = defaults(gg.labels, new_labels)
        return gg

    def _make_layer(self):
        kwargs = self._cache['kwargs']
        DP = self.DEFAULT_PARAMS
        lkwargs = {'geom': self,
                   'mapping': kwargs['mapping'],
                   'data': kwargs['data'],
                   'stat': self._stat,
                   'position': kwargs.get('position',
                                          DP['position'])}

        for param in ('show_legend', 'inherit_aes'):
            if param in kwargs:
                lkwargs[param] = kwargs[param]
            else:
                with suppress(KeyError):
                    lkwargs[param] = DP[param]

        return layer(**lkwargs)

    def _make_stat(self):
        """
        Return stat instance for this geom

        Create a stat if none has been passed in the
        kwargs
        """
        kwargs = self._cache['kwargs']
        with suppress(KeyError):
            if isinstance(kwargs['stat'], stat):
                return kwargs['stat']

        name = 'stat_{}'.format(
            kwargs.get('stat', self.DEFAULT_PARAMS['stat']))
        stat_klass = gg_import(name)
        recognized = ((stat_klass.aesthetics() |
                       stat_klass.DEFAULT_PARAMS.viewkeys()) &
                      kwargs.viewkeys())
        stat_params = {}
        for p in recognized:
            stat_params[p] = kwargs[p]
        return stat_klass(geom=self.__class__.__name__[5:],
                          **stat_params)

    def _sanitize_arguments(self, args, kwargs):
        """
        Return kwargs with the mapping and data values
        """
        mapping, data = {}, None
        aes_err = ('Found more than one aes argument. '
                   'Expecting zero or one')
        data_err = 'More than one dataframe argument'

        # check args #
        for arg in args:
            if isinstance(arg, aes) and mapping:
                raise GgplotError(aes_err)
            if isinstance(arg, pd.DataFrame) and data:
                raise GgplotError(data_err)

            if isinstance(arg, aes):
                mapping = arg
            elif isinstance(arg, pd.DataFrame):
                data = arg
            else:
                msg = "Unknown argument of type '{0}'."
                raise GgplotError(msg.format(type(arg)))

        # check kwargs #
        # kwargs mapping has precedence over that in args
        if 'mapping' not in kwargs:
            kwargs['mapping'] = mapping

        if data is not None and 'data' in kwargs:
            raise GgplotError(data_err)
        elif 'data' not in kwargs:
            kwargs['data'] = data

        duplicates = set(kwargs['mapping']) & set(kwargs)
        if duplicates:
            msg = 'Aesthetics {} specified two times.'
            raise GgplotError(msg.format(duplicates))
        return kwargs

    def verify_arguments(self, kwargs):
        unknown = (kwargs.viewkeys() -
                   self.aesthetics() -                    # geom aesthetics
                   self.DEFAULT_PARAMS.viewkeys() -       # geom parameters
                   {'data', 'mapping'} -                  # layer parameters
                   {'show_legend', 'inherit_aes'} -       # layer parameters
                   self._stat.aesthetics() -              # stat aesthetics
                   self._stat.DEFAULT_PARAMS.viewkeys())  # stat parameters
        if unknown:
            msg = 'Unknown parameters {}'
            raise GgplotError(msg.format(unknown))

    def _make_pinfos(self, data, params):
        units = []
        for col in data.columns:
            if col in self._units:
                units.append(col)

        shrinkable = {'alpha', 'fill', 'color', 'size', 'linetype',
                      'shape', 'outlier_shape'}

        def prep(pinfo):
            """
            Reduce shrinkable parameters &  append zorder
            """
            # If it is the same value in the list make it a scalar
            # This can help the matplotlib functions draw faster
            for ae in set(pinfo) & shrinkable:
                with suppress(TypeError, IndexError):
                    if all(pinfo[ae][0] == v for v in pinfo[ae]):
                        pinfo[ae] = pinfo[ae][0]
            pinfo['zorder'] = params['zorder']
            return pinfo

        out = []
        if units:
            # Currently groupby does not like None values in any of
            # the columns that participate in the grouping. These
            # Nones come in when the default aesthetics are added to
            # the data. We drop these columns and after turning the
            # the dataframe into a dictionary insert a None for that
            # aesthetic
            _units = []
            _none_units = []
            for unit in units:
                if data[unit].iloc[0] is None:
                    _none_units.append(unit)
                    del data[unit]
                else:
                    _units.append(unit)

            for name, _data in data.groupby(_units):
                pinfo = _data.to_dict('list')
                for ae in _units:
                    pinfo[ae] = pinfo[ae][0]
                for ae in _none_units:
                    pinfo[ae] = None
                out.append(prep(pinfo))
        else:
            pinfo = data.to_dict('list')
            out.append(prep(pinfo))

        return out

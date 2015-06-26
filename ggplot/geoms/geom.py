from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from copy import deepcopy

import pandas as pd

from ..components.aes import aes, make_labels
from ..components.layer import layer
from ..utils.exceptions import GgplotError
from ..utils import is_scalar_or_string, gg_import, defaults, suppress

__all__ = ['geom']
__all__ = [str(u) for u in __all__]


class geom(object):
    """Base class of all Geoms"""
    DEFAULT_AES = dict()
    REQUIRED_AES = set()
    DEFAULT_PARAMS = dict()

    data = None           # geom/layer specific dataframe
    aes = None            # mappings i.e aes(x=col1, fill=col2, ...)
    manual_aes = None     # setting of aesthetic
    params = None         # parameter settings

    # The geom responsible for the legend if draw_legend is
    # not implemented
    guide_geom = 'point'

    # Some geoms require more information than that provided by the
    # user. This information is usually another aesthetic variable
    # but it could another non-aesthetic variable. It is the duty
    # of the associated statistic to calculate this information.
    #
    # For example:
    #   A geom may have REQUIRED_AES = {'x', 'y'} and
    #   the user may map or manually set only aesthetic 'x',
    #   so the stat would have to calculate 'y'. However this
    #   may not be enough, to actually make the plot the geom
    #   may require the 'width' aesthetic. In this case, 'width'
    #   would be the extra required information.
    #
    # geoms should fill out this set with what they require
    # and is not in REQUIRED_AES
    # see: geom_bar, stat_bin
    _extra_requires = set()

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
        self._cache = {}
        self.valid_aes = set(self.DEFAULT_AES) ^ self.REQUIRED_AES
        self.aes, self.data, kwargs = self._find_aes_and_data(args, kwargs)

        # This set will list the geoms that were uniquely set in this
        # geom (not specified already i.e. in the ggplot aes).
        self.aes_unique_to_geom = set(self.aes.keys())

        with suppress(KeyError):
            kwargs['color'] = kwargs.pop('colour')

        # When a geom is created, some of the parameters may be meant
        # for the stat and some for the layer.
        # Some arguments are can be identified as either aesthetics to
        # the geom and or parameter settings to the stat, in this case
        # if the argument has a scalar value it is a setting for the stat.
        stat_params = {}
        self.params = deepcopy(self.DEFAULT_PARAMS)
        self.manual_aes = {}
        layer_params = {}
        _layer_params = ['group', 'show_guide', 'inherit_aes']
        for p in layer_params:
            with suppress(KeyError):
                self._layer_params[p] = self.params.pop(p)

        stat_type = self._cache['stat_type']
        stat_aes_params = (set(stat_type.DEFAULT_PARAMS) |
                           stat_type.REQUIRED_AES)
        for k, v in kwargs.items():
            if k in self.aes:
                raise GgplotError('Aesthetic, %s, specified twice' % k)
            # geom recognizes aesthetic but stat wants it as a parameter,
            # if it is a scalar the stat takes it
            elif (k in self.valid_aes and
                  k in stat_type.DEFAULT_PARAMS and
                  is_scalar_or_string(kwargs[k])):
                stat_params[k] = v
            # geom mapping
            elif k in self.valid_aes:
                self.manual_aes[k] = v
            # layer parameters
            elif k in _layer_params:
                layer_params[k] = kwargs[k]
            # Override default geom parameters
            elif k in self.DEFAULT_PARAMS:
                self.params[k] = v
            # stat parameters
            elif k in stat_aes_params:
                stat_params[k] = v
            else:
                raise GgplotError('Cannot recognize argument: %s' % k)

        self._cache['stat_params'] = stat_params
        self._cache['layer_params'] = layer_params

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

    @staticmethod
    def reparameterise(data):
        return data

    def draw_groups(self, data, scales, coordinates, ax, **params):
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
        coordinates : coord
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
                self.draw(pinfo, scales, coordinates, ax, **params)

    @staticmethod
    def draw(pinfo, scales, coordinates, ax, **params):
        msg = "The geom should implement this method."
        raise NotImplementedError(msg)

    @property
    def _stat(self):
        """
        Return stat instance for this geom

        The stat is created once and stored in the cache.
        The stat can only be created after the geom has
        been initialized.

        Alternatively a stat not automatically created by
        the geom can add itself to the geoms cache.
        See stat._geom
        """
        try:
            stat = self._cache['stat']
        except KeyError:
            stat = self._cache['stat_type'](
                geom=self.__class__.__name__[5:],
                position=self.params['position'],
                **self._cache['stat_params'])
            self._cache['stat'] = stat
        return stat

    def _get_stat_type(self, kwargs):
        """
        Find out the stat and return the type object that can be
        used(called) to create it.
        For example, if the stat is 'smooth' we return
        ggplot.stats.stat_smooth
        """
        name = 'stat_{}'.format(
            kwargs.get('stat', self.DEFAULT_PARAMS['stat']))
        self._cache['stat_type'] = gg_import(name)
        return self._cache['stat_type']

    def __radd__(self, gg):
        gg = deepcopy(gg)
        # create and add layer
        l = layer(geom=self,
                  stat=self._stat,
                  data=self.data,
                  mapping=self.aes,
                  position=self.params['position'],
                  **self._cache['layer_params'])
        gg.layers.append(l)

        # Add any new labels
        mapping = make_labels(self.aes)
        default = make_labels(self._stat.DEFAULT_AES)
        new_labels = defaults(mapping, default)
        gg.labels = defaults(gg.labels, new_labels)
        return gg

    def _find_aes_and_data(self, args, kwargs):
        """
        Identify the aes and data objects.

        Return a dictionary of the aes mappings and
        the data object.

        - args is a list
        - kwargs is a dictionary

        Note: This is a helper function for self.__init__
        It modifies the kwargs
        """
        passed_aes = {}
        data = None
        aes_err = ('Found more than one aes argument. '
                   'Expecting zero or one')

        for arg in args:
            if isinstance(arg, aes) and passed_aes:
                raise GgplotError(aes_err)
            if isinstance(arg, aes):
                passed_aes = arg
            elif isinstance(arg, pd.DataFrame):
                data = arg
            else:
                msg = "Unknown argument of type '{0}'."
                raise GgplotError(msg.format(type(arg)))

        if 'mapping' in kwargs and passed_aes:
            raise GgplotError(aes_err)
        elif not passed_aes and 'mapping' in kwargs:
            passed_aes = kwargs.pop('mapping')

        if data is None and 'data' in kwargs:
            data = kwargs.pop('data')

        _aes = {}
        # To make mapping of columns to geom/stat or stat parameters
        # possible
        stat = self._get_stat_type(kwargs)
        _keep = set(self.DEFAULT_PARAMS) | set(stat.DEFAULT_PARAMS)
        _keep.update(stat.DEFAULT_AES)
        _keep.update(stat.REQUIRED_AES)
        _keep.add('group')
        for k, v in passed_aes.items():
            if k in self.valid_aes or k in _keep:
                _aes[k] = v
        return _aes, data, kwargs

    def _make_pinfos(self, data, kwargs):
        """
        Make plot information

        Put together the data and the default aesthetics into
        groups that can be plotted in a single call to self.draw

        Parameters
        ----------
        data : dataframe
            The data to be split into groups
        kwargs : dict
            kwargs passed to the draw or draw_groups methods

        Returns
        -------
        out : list of dict
            Each dict represents a unique grouping, ready for
            plotting
            The dicts are of the form
            {'column-name' | 'mpl-param-name': list-of-values | value}

        Note
        ----
        This is a helper function for self.draw_group or self.draw
        """
        # (default aesthetics + data), grouped into plottable units
        units = []
        for col in data.columns:
            if col in self._units:
                units.append(col)

        shrinkable = {'alpha', 'fill', 'color', 'size', 'linetype'}

        def shrink(pinfo):
            """
            Reduce shrinkable parameters to scalars if possible.
            """
            # If it is the same value in the list make it a scalar
            # This can help the matplotlib functions draw faster
            for ae in set(pinfo) & shrinkable:
                with suppress(TypeError, IndexError):
                    if all(pinfo[ae][0] == v for v in pinfo[ae]):
                        pinfo[ae] = pinfo[ae][0]
            return pinfo

        def prep(pinfo):
            """
            After data has been converted to a dict of lists
            prepare it for plotting
            """
            pinfo.update(self.manual_aes)
            pinfo = shrink(pinfo)
            pinfo['zorder'] = kwargs['zorder']
            return pinfo

        out = []
        if units:
            for name, _data in data.groupby(units):
                pinfo = deepcopy(self.DEFAULT_AES)
                pinfo.update(_data.to_dict('list'))
                for ae in units:
                    pinfo[ae] = pinfo[ae][0]

                out.append(prep(pinfo))
        else:
            pinfo = deepcopy(self.DEFAULT_AES)
            pinfo.update(data.to_dict('list'))
            out.append(prep(pinfo))

        return out

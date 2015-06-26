from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from copy import deepcopy

import pandas as pd

from ..utils import uniquecols, gg_import
from ..utils.exceptions import GgplotError

__all__ = ['stat']
__all__ = [str(u) for u in __all__]


class stat(object):
    """Base class of all stats"""
    REQUIRED_AES = set()
    DEFAULT_AES = dict()
    DEFAULT_PARAMS = dict()

    # Should the values produced by the statistic also
    # be transformed in the second pass when recently
    # added statistics are trained to the scales
    retransform = True

    # Stats may modify existing columns or create extra
    # columns.
    #
    # Any extra columns that may be created by the stat
    # should be specified in this set
    # see: stat_bin
    CREATES = set()

    def __init__(self, *args, **kwargs):
        _params, kwargs = self._find_stat_params(kwargs)
        self.params = deepcopy(self.DEFAULT_PARAMS)
        self.params.update(_params)

        self._cache = {}
        # Whatever arguments cannot be recognised as
        # parameters, will be used to create a geom
        self._cache['args'] = args
        self._cache['kwargs'] = kwargs

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

    @classmethod
    def _calculate(cls, data, scales, **params):
        msg = "{} should implement this method."
        raise NotImplementedError(
            msg.format(cls.__name__))

    @classmethod
    def _calculate_groups(cls, data, scales, **params):
        """
        Calculate the stats of all the groups and
        return the results in a single dataframe.

        This is a default function that can be overriden
        by individual stats

        Parameters
        ----------
        data : dataframe
            data for the computing
        scales : namedtuple
            x & y scales
        params : dict
            The parameters for the stat. It includes default
            values if user did not set a particular parameter.
        """
        if not len(data):
            return pd.DataFrame()

        stats = []
        for _, old in data.groupby('group'):
            new = cls._calculate(old, scales, **params)
            unique = uniquecols(old)
            missing = unique.columns.difference(new.columns)
            u = unique.loc[[0]*len(new), missing].reset_index(drop=True)
            # concat can have problems with empty dataframes that
            # have an index
            if u.empty and len(u):
                u = pd.DataFrame()

            df = pd.concat([new, u], axis=1)
            stats.append(df)

        stats = pd.concat(stats, axis=0, ignore_index=True)

        # Note: If the data coming in has columns with non-unique
        # values with-in group(s), this implementation loses the
        # columns. Individual stats may want to do some preparation
        # before then fall back on this implementation or override
        # it completely.
        return stats

    def __radd__(self, gg):
        return gg + self._geom

    @property
    def _geom(self):
        """
        Create a geom

        The geom is created once and stored in the cache.
        The geom can only be created after the stat has
        been initialized.
        """
        try:
            _geom = self._cache['geom']
        except KeyError:
            # Create a geom and it to the ggplot object
            geom = gg_import('geom_{}'.format(self.params['geom']))
            _geom = geom(*self._cache['args'],
                         stat=self.__class__.__name__[5:],
                         position=self.params['position'],
                         **self._cache['kwargs'])
            # Allow the geom to know about the stat object
            # Usefull in geom.__radd__ when creating layer
            _geom._cache['stat'] = self
            self._cache['geom'] = _geom
        return _geom

    def _find_stat_params(self, kwargs):
        """
        Identity and return the stat parameters.

        The identified parameters are removed from kwargs

        Parameters
        ----------
        kwargs : dict
            keyword arguments passed to stat.__init__

        Returns
        -------
        d : dict
            stat parameters
        kwargs : dict
            rest of the kwargs
        """
        d = {}
        for k in list(kwargs.keys()):
            if (k in self.DEFAULT_PARAMS or
                    k in self.REQUIRED_AES):
                d[k] = kwargs.pop(k)
        return d, kwargs

    def _verify_aesthetics(self, data):
        """
        Check if all the required aesthetics have been specified

        Raise an Exception if an aesthetic is missing
        """
        missing_aes = self.REQUIRED_AES - set(data.columns)
        if missing_aes:
            msg = '{} requires the following missing aesthetics: {}'
            raise GgplotError(msg.format(
                self.__class__.__name__, ', '.join(missing_aes)))

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import sys
from copy import deepcopy

import pandas as pd

from ..layer import layer
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

    # used by _print_warning to keep track of the
    # warning messages printed to the standard error
    _warnings_printed = set()

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

    def _print_warning(self, message):
        """
        Prints message to the standard error.
        """
        if message not in self._warnings_printed:
            sys.stderr.write(message)
            self._warnings_printed.add(message)

    def _calculate(self, data, scales, **kwargs):
        msg = "{} should implement this method."
        raise NotImplementedError(
            msg.format(self.__class__.__name__))

    def _calculate_groups(self, data, scales, **kwargs):
        """
        Calculate the stats of all the groups and
        return the results in a single dataframe.

        This is a default function that can be overriden
        by individual stats
        """
        if not len(data):
            return pd.DataFrame()

        stats = []
        for _, old in data.groupby('group'):
            new = self._calculate(old, scales)
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
        # Create a geom and it to the ggplot object
        _g = gg_import('geom_' + self.params['geom'])
        _geom = _g(*self._cache['args'], **self._cache['kwargs'])
        _geom.params['stat'] = self.__class__.__name__[5:]
        _geom.params['position'] = self.params['position']
        _geom._stat = self
        return gg + _geom

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
            if k in self.DEFAULT_PARAMS:
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

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from copy import deepcopy

import pandas as pd

from ..utils import uniquecols, gg_import, check_required_aesthetics
from ..utils import groupby_apply, copy_keys
from ..utils.exceptions import GgplotError


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
        self.params = copy_keys(kwargs, deepcopy(self.DEFAULT_PARAMS))

        # Will be used to create the geom
        self._cache = {'args': args, 'kwargs': kwargs}

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

    def setup_params(self, data):
        """
        Overide this to verify parameters
        """
        return self.params

    @classmethod
    def compute_layer(cls, data, params, panel):
        check_required_aesthetics(
            cls.REQUIRED_AES,
            list(data.columns) + list(params.keys()),
            cls.__name__)

        def fn(pdata):
            """
            Helper compute function
            """
            # Given data belonging to a specific panel, grab
            # the corresponding scales and call the method
            # that does the real computation
            pscales = panel.panel_scales(pdata['PANEL'].iat[0])
            return cls.compute_panel(pdata, pscales, **params)

        return groupby_apply(data, 'PANEL', fn)

    @classmethod
    def compute_panel(cls, data, scales, **params):
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
            new = cls.compute_group(old, scales, **params)
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

    @classmethod
    def compute_group(cls, data, scales, **params):
        msg = "{} should implement this method."
        raise NotImplementedError(
            msg.format(cls.__name__))

    def __radd__(self, gg):
        geom = gg_import('geom_{}'.format(self.params['geom']))
        _geom = geom(*self._cache['args'],
                     stat=self,
                     **self._cache['kwargs'])
        return gg + _geom

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

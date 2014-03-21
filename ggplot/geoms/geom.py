from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from copy import deepcopy
from ggplot.components import aes
from pandas import DataFrame

__all__ = ['geom']
__all__ = [str(u) for u in __all__]

class geom(object):
    """Base class of all Geoms"""
    VALID_AES = {}
    REQUIRED_AES = set()
    DEFAULT_PARAMS = dict()

    data = None
    aes = None
    manual_aes = None
    params = None

    _groups = set()
    _translations = dict()

    def __init__(self, *args, **kwargs):
        # new dicts for each geom
        self.aes, self.data = self._aes_and_data(args, kwargs)
        self.manual_aes = {}
        self.params = deepcopy(self.DEFAULT_PARAMS)
        for k, v in kwargs.items():
            if k in self.VALID_AES:
                self.manual_aes[k] = v
            elif k in self.DEFAULT_PARAMS:
                self.params[k] = v


    def plot_layer(self, data, ax):
        # NOTE: This is the correct check however with aes
        # set in ggplot(), self.aes is empty
        # groups = groups & set(self.aes) & set(data.columns)
        try:
            groups = self._groups & set(data.columns)
        except AttributeError:
            groups = set()

        for _data in self._get_grouped_data(data, groups):
            _data = dict((k, v) for k, v in _data.items()
                         if k in self.VALID_AES)
            _data.update(self.manual_aes)
            self._rename_aes(_data)
            self.plot(_data, ax)

    def __radd__(self, gg):
        gg = deepcopy(gg)
        gg.geoms.append(self)
        return gg

    def _verify_aesthetics(self, layer):
        """
        Check if all the required aesthetics have been specified

        Raise an Exception if an aesthetic is missing
        """
        missing_aes = self.REQUIRED_AES - set(layer)
        if missing_aes:
            msg = '{} requires the following missing aesthetics: {}'
            raise Exception(msg.format(
                self.__class__.__name__, ', '.join(missing_aes)))

    def _aes_and_data(self, args, kwargs):
        """
        Identify the aes and data objects.

        Return a dictionary of the aes mappings and
        the data object.

        - args is a list
        - kwargs is a dictionary

        Note: This is a helper function for self.__init__
        """
        passed_aes = {}
        data = None
        aes_err = 'Found more than one aes argument. Expecting zero or one'

        for arg in args:
            if isinstance(arg, aes) and passed_aes:
                raise Execption(aes_err)
            if isinstance(arg, aes):
                passed_aes = arg
            elif isinstance(arg, DataFrame):
                data = arg
            else:
                raise Exception('Unknown argument of type "{0}".'.format(type(arg)))

        if 'mapping' in kwargs and passed_aes:
            raise Exception(aes_err)
        elif not passed_aes and 'mapping' in kwargs:
            passed_aes = kwargs['mapping']

        if data is None and 'data' in kwargs:
            data = kwargs['data']

        valid_aes = {}
        for k, v in passed_aes.items():
            if k in self.VALID_AES:
               valid_aes[k] = v
        return valid_aes, data

    def _rename_aes(self, layer):
        """
        Convert ggplot2 API names to matplotlib names
        """
        # apply to all geoms
        _translations = {'colour': 'color', 'linetype': 'linestyle'}

        def _rename_fn(old, new):
            if old in layer:
                layer[new] = layer.pop(old)

        for k, v in _translations.items():
            _rename_fn(k, v)
        for k, v in self._translations.items():
            _rename_fn(k, v)

    def _get_grouped_data(self, data, groups):
        """
        Split the data into groups.

        Parameters
        ----------
        data   : dataframe
            The data to be split into groups
        groups : set
            A set of column names in the data and by
            which the grouping will happen

        Returns
        -------
        res : list
            A list of dicts. Each dict represents a unique
            grouping. The dicts are of the form
            {'column-name': list-of-values | value}

        Note
        ----
        This is a helper function for the geoms. If the column
        names in the data represent valid arguments to a matplotlib
        function, then the dict(s) returned can be passed along to
        the plot command as **kwarg.
        """
        out = []
        if groups:
            for name, _data in data.groupby(list(groups)):
                _data = _data.to_dict('list')
                for ae in groups:
                    _data[ae] = _data[ae][0]
                out.append(_data)
        else:
            _data = data.to_dict('list')
            out.append(_data)
        return out


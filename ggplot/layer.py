from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import six
import pandas.core.common as com

from .components.aes import aes, is_calculated_aes
from .scales.scales import scales_add_defaults
from .utils.exceptions import GgplotError


class layer(object):

    def __init__(self, geom=None, stat=None,
                 data=None, mapping=None,
                 position=None, params=None,
                 inherit_aes=False, group=None):
        self.geom = geom
        self.stat = stat
        self.data = data
        self.mapping = mapping
        self.position = position
        self.params = params
        self.inherit_aes = inherit_aes
        self.group = group

    def layer_mapping(self, mapping):
        """
        Return the mappings that are active in this layer
        """
        # For certain geoms, it is useful to be able to
        # ignore the default aesthetics and only use those
        # set in the layer
        if self.inherit_aes:
            # TODO: Changing this accordingly
            aesthetics = mapping
        else:
            aesthetics = mapping

        # drop aesthetics that are manual or calculated
        manual = set(self.geom.manual_aes.keys())
        calculated = set(is_calculated_aes(aesthetics))
        d = dict((ae, v) for ae, v in aesthetics.items()
                 if not (ae in manual) and not (ae in calculated))
        return aes(**d)


    def compute_aesthetics(self, data, plot):
        """
        Return a dataframe where the columns match the
        aesthetic mappings
        """
        aesthetics = self.layer_mapping(plot.mapping)

        # Override grouping if set in layer.
        if not self.group is None:
            aesthetics['group'] = self.group

        scales_add_defaults(plot.scales, data, aesthetics)

        renames = {}   # columns to rename with aesthetics names
        settings = {}  # for manual settings withing aesthetics
        for ae, col in aesthetics.items():
            if isinstance(col, six.string_types):
                renames[col] = ae
            elif com.is_list_like(col):
                n = len(col)
                if n != len(data) or n != 1:
                    raise GgplotError(
                        "Aesthetics must either be length one, " +
                        "or the same length as the data")
                settings[ae] = col
            else:
                msg = "Do not know how to deal with aesthetic `{}`"
                raise GgplotError(msg.format(ae))

        evaled = data.loc[:, list(renames.keys())]
        evaled.rename(columns=renames, inplace=True)
        evaled.update(settings)

        if len(data) == 0 and settings:
            # No data, and vectors suppled to aesthetics
            evaled['PANEL'] = 1
        else:
            evaled['PANEL'] = data['PANEL']

        return evaled

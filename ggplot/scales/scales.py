from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import itertools

import numpy as np
import pandas as pd
import pandas.core.common as com

from ..utils import discrete_dtypes, continuous_dtypes
from ..utils import gg_import
from ..utils.exceptions import gg_warning

_TPL_DUPLICATE_SCALE = """\
Scale for '{0}' is already present.
Adding another scale for '{0}',
which will replace the existing scale.
"""


class Scales(list):

    def append(self, sc):
        """
        Add scale 'sc' and remove any previous
        scales that cover the same aesthetics
        """
        ae = sc.aesthetics[0]
        cover_ae = self.find(ae)
        if any(cover_ae):
            gg_warning(_TPL_DUPLICATE_SCALE.format(ae))
            idx = cover_ae.index(True)
            self.remove(idx)
        # super() does not work well with reloads
        list.append(self, sc)

    def find(self, aesthetic):
        """
        Return a list of True|False for each scale if
        it covers the aesthetic.
        """
        return [aesthetic in s.aesthetics for s in self]

    def input(self):
        """
        Return a list of all the aesthetics covered by
        the scales.
        """
        lst = [s.aesthetics for s in self]
        return list(itertools.chain(*lst))

    def get_scales(self, aesthetic):
        """
        Return the scale for the aesthetic or None if there
        isn't one.
        """
        bool_lst = self.find(aesthetic)
        try:
            idx = bool_lst.index(True)
            return self[idx]
        except ValueError:
            return None

    def non_position_scales(self):
        """
        Return a list of the non-position scales that
        are present
        """
        l = [s for s in self
             if not ('x' in s.aesthetics) and not ('y' in s.aesthetics)]
        return Scales(l)

    def train(self, data, vars, idx):
        """
        Train the scales on the data.
        The scales should be for the same aesthetic
        e.g. x scales, y scales, color scales, ...

        Parameters
        ----------
        data : dataframe
            data to use for training
        vars : list | tuple
            columns in data to use for training
        idx : array-like
            indices that map the data points to the
            scales. These start at 1, so subtract 1 to
            get the true index into the scales array
        """
        idx = np.asarray(idx)
        for col in vars:
            for i, sc in enumerate(self, start=1):
                bool_idx = (i == idx)
                sc.train(data.loc[bool_idx, col])

    def map(self, data, vars, idx):
        """
        Map the data on the scales
        The scales should be for the same aesthetic
        e.g. x scales, y scales, color scales, ...

        Parameters
        ----------
        data : dataframe
            data with columns to map
            This is modified inplace
        vars : list | tuple
            columns to map
        idx : array-like
            indices that link the data points to the
            scales. These start at 1, so subtract 1 to
            get the true index into the scales array
        """
        idx = np.asarray(idx)
        # discrete scales can change the dtype
        # from category to int. Use a new dataframe
        # to collect these results
        df = pd.DataFrame({}, index=range(len(data)))
        cat_cols = []

        # Loop through each variable, mapping across each scale,
        # then joining back into the copy of the data
        for col in vars:
            use_df = com.is_categorical_dtype(data[col])
            if use_df:
                cat_cols.append(col)
            for i, sc in enumerate(self, start=1):
                bool_idx = (i == idx)
                results = sc.map(data.loc[bool_idx, col])
                if use_df:
                    df.loc[bool_idx, col] = results
                else:
                    data.loc[bool_idx, col] = results

        for col in cat_cols:
            data[col] = df[col]


def scales_add_defaults(scales, data, aesthetics):
    """
    Add default scales for the aesthetics if none are
    present

    Scales are added only if the aesthetic is mapped to
    a column in the dataframe. This function may have to be
    called separately after evaluating the aesthetics.
    """
    if not aesthetics:
        return

    # aesthetics with scales
    if scales:
        aws = reduce(set.union, map(set, [sc.aesthetics for sc in scales]))
    else:
        aws = set()

    # aesthetics that do not have scales present
    new_aesthetics = set(aesthetics.keys()) - aws
    if not new_aesthetics:
        return

    ae_cols = [(ae, aesthetics[ae]) for ae in new_aesthetics
               if aesthetics[ae] in data.columns]

    for ae, col in ae_cols:
        _type = scale_type(data[col])
        scale_name = 'scale_{}_{}'.format(ae, _type)
        scale_f = gg_import(scale_name)
        if scale_f is None:
            # Skip aesthetics with no scales (e.g. group, order, etc)
            continue
        scales.append(scale_f())

    return scales


def scales_add_missing(plot, aesthetics):
    """
    Add missing but required scales.

    Parameters
    ----------
    aesthetics : list | tuple
        aesthetic names. Typically, ('x', 'y').
    """

    # Keep only aesthetics that aren't already in plot$scales
    aesthetics = set(aesthetics) - set(plot.scales.input())

    for ae in aesthetics:
        scale_name = 'scale_{}_continuous'.format(ae)
        scale_f = gg_import(scale_name)
        plot.scales.append(scale_f())


def scale_type(column):
    if column.dtype in continuous_dtypes:
        stype = 'continuous'
    elif column.dtype in discrete_dtypes:
        stype = 'discrete'
    elif column.dtype == np.dtype('<M8[ns]'):
        stype = 'datetime'
    else:
        msg = """\
            Don't know how to automatically pick scale for \
            object of type {}. Defaulting to 'continuous'"""
        gg_warning(msg.format(column.dtype))
        stype = 'continuous'
    return stype

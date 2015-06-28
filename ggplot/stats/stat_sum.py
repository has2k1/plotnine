from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from ..components.aes import all_aesthetics
from ..utils import groupby_apply
from .stat import stat


class stat_sum(stat):
    """
    Sum unique values.  Useful for overplotting on scatterplots.
    """
    REQUIRED_AES = {'x', 'y'}
    DEFAULT_PARAMS = {'geom': 'point', 'position': 'identity'}
    DEFAULT_AES = {'size': '..prop..'}  # options: ..prop.., ..n..
    CREATES = {'size'}

    @classmethod
    def _calculate_groups(cls, data, scales, **params):
        if 'weight' not in data:
            data['weight'] = params.get('weight', 1)

        def count(df):
            """
            Do a weighted count
            """
            df['n'] = df['weight'].sum()
            return df.iloc[0:1]

        def ave(df):
            """
            Calculate proportion values
            """
            df['prop'] = df['n']/df['n'].sum()
            return df

        # group by all present aesthetics other than the weight,
        # then sum them (i.e no. of uniques) to get the raw count
        # 'n', and the proportions 'prop' per group
        group_by = (set(data.columns) & all_aesthetics) - {'weight'}
        group_by = list(group_by)
        counts = groupby_apply(data, group_by, count)
        counts = groupby_apply(counts, 'group', ave)
        return counts

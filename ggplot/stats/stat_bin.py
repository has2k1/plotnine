from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import sys
from .stat import stat
import numpy as np
import pandas as pd
import matplotlib.cbook as cbook


class stat_bin(stat):
    REQUIRED_AES = {'x'}
    DEFAULT_PARAMS = {'geom': 'bar', 'position': 'stack',
                      'width': 0.9, 'drop': False, 'right': False,
                      'binwidth': None, 'origin': None, 'breaks': None}

    # Maybe should be an internal API thing, especially
    # the width
    CREATES = {'x', 'y', 'width'}

    def __init__(self, *args, **kwargs):
        super(stat_bin, self).__init__(*args, **kwargs)
        self._warning_printed = False

    def _calculate(self, pinfo):
        x = pinfo.pop('x')
        breaks = self.params['breaks']
        right = self.params['right']
        binwidth = self.params['binwidth']

        # TODO: make sure it is passed from the geom
        # pinfo.pop('weight')
        weight = 1
        x_weights = np.ones(len(x)) * weight

        # TODO: Expand the coverage and maybe make it
        # available in the utilities
        def _is_categorical(lst):
            if cbook.is_sequence_of_strings(lst):
                return True
            return False

        categorical = _is_categorical(x)

        if categorical:
            x_assignments = x
            _width = self.params['width']
            pinfo['x'] = sorted(set(x))
        elif cbook.is_numlike(x[0]):
            if breaks is None and binwidth is None:
                _bin_count = 30
                if not self._warning_printed:
                    sys.stderr.write(
                        "stat_bin: binwidth defaulted to range/30." +
                        " Use 'binwidth = x' to adjust this.")
                    self._warning_printed = True
            if binwidth:
                _bin_count = int(np.ceil(np.ptp(x))) / binwidth

            # Breaks have a higher precedence and,
            # pandas accepts either the breaks or the number of bins
            _bins_info = breaks or _bin_count
            x_assignments, breaks = pd.cut(x, bins=_bins_info, labels=False,
                                           right=right, retbins=True)
            _width = np.diff(breaks)
            pinfo['x'] = [breaks[i] + _width[i] / 2
                          for i in range(len(breaks)-1)]
        else:
            # TODO: Create test case
            raise Exception("Cannot recognise the type of x")

        # Create a dataframe with two columns:
        #   - the bins to which each x is assigned
        #   - the weights of each x value
        # Then create a weighted frequency table
        _df = pd.DataFrame({'assignments': x_assignments,
                            'weights': x_weights
                            })
        _wfreq_table = pd.pivot_table(_df, values='weights',
                                      rows=['assignments'], aggfunc=np.sum)

        # For numerical x values, empty bins get have no value
        # in the computed frequency table.
        # The frequency table is a Series object, we need to keep it ordered
        if len(_wfreq_table) < len(pinfo['x']):
            empty_bins = set(range(max(x_assignments))) - set(x_assignments)
            for _b in empty_bins:
                _wfreq_table[_b] = 0
            _wfreq_table = _wfreq_table.sort_index()

        pinfo['y'] = list(_wfreq_table)
        pinfo['width'] = _width
        return pinfo

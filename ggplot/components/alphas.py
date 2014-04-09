from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np


def assign_alphas(data, aes):
    """
    Assigns alpha values to the given data based
    on the aes creates an appropriate legend entry

    The mapped alpha values fall in the closed range [0.1, 1]

    Parameters
    ----------
    data : DataFrame
        dataframe which should have alpha values assigned to
    aes : aesthetic
        mapping, including a mapping from alpha values to variable

    Returns
    -------
    data : DataFrame
        the changed dataframe
    legend_entry : dict
        An entry into the legend dictionary.
        Documented in `components.legend`
    """
    legend_entry = dict()
    if 'alpha' in aes:
        alpha_col = aes['alpha']
        values = data[alpha_col].astype(np.float)
        _min, _max = values.min(), values.max()
        data[':::alpha_mapping:::'] = np.interp(values,
                                                [_min, _max], [0.1, 1])
        labels = np.percentile(values, [5, 25, 50, 75, 95])
        quantiles = np.percentile(data[':::alpha_mapping:::'],
                                  [5, 25, 50, 75, 95])
        legend_entry = {
            'column_name': alpha_col,
            'dict': dict(zip(quantiles, labels)),
            'scale_type': 'continuous'}
    return data, legend_entry

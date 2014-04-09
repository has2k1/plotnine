from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np


def assign_sizes(data, aes):
    """Assigns size to the given data based on the aes and adds the right legend

    Parameters
    ----------
    data : DataFrame
        dataframe which should have sizes assigned to
    aes : aesthetic
        mapping, including a mapping from sizes to variable

    Returns
    -------
    data : DataFrame
        the changed dataframe
    legend_entry : dict
        An entry into the legend dictionary.
        Documented in `components.legend`
    """
    legend_entry = dict()
    # We need to normalize size so that the points aren't really big or
    # really small.
    # TODO: add different types of normalization (log, inverse, etc.)
    if 'size' in aes:
        size_col = aes['size']
        values = data[size_col].astype(np.float)
        _min = values.min()
        data[":::size_mapping:::"] = (200.0 *
                                      (values - _min + .15) /
                                      (values.max() - _min))
        labels = np.percentile(values, [5, 25, 50, 75, 95])
        quantiles = np.percentile(data[":::size_mapping:::"],
                                  [5, 25, 50, 75, 95])

        legend_entry = {
            'column_name': size_col,
            'dict': dict(zip(quantiles, labels)),
            'scale_type': 'continuous'}
    return data, legend_entry

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
from .legend import get_labels
from ..utils.exceptions import GgplotError


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
        # Check that values are in the right format
        try :
            values = data[alpha_col].astype(np.float)
        except ValueError :
            raise GgplotError(
                "Size aesthetic '%s' contains non-numerical data" % alpha_col)
        labels, scale_type, indices = get_labels(data, alpha_col)
        _min, _max = values.min(), values.max()
        normalize = lambda v : np.interp(v, [_min, _max], [0.1, 1])
        data[':::alpha_mapping:::'] = normalize(values)
        if scale_type == "continuous" :
            quantiles = np.percentile(data[':::alpha_mapping:::'], indices)
        elif scale_type == "discrete" :
            quantiles = normalize(np.array(labels, dtype=np.float))
        legend_entry = {
            'column_name': alpha_col,
            'dict': dict(zip(quantiles, labels)),
            'scale_type': scale_type}
    return data, legend_entry

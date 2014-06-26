from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
from .legend import get_labels
from ..utils.exceptions import GgplotError


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
        # Check that values are in the right format
        try :
            values = data[size_col].astype(np.float)
        except ValueError :
            raise GgplotError(
                "Size aesthetic '%s' contains non-numerical data" % size_col)
        _min = values.min()
        normalize = lambda v : 30 + (200.0 * (v - _min) / (v.max() - _min))
        data[":::size_mapping:::"] = normalize(values)
        labels, scale_type, indices = get_labels(data, size_col)
        if scale_type == "continuous" :
            quantiles = np.percentile(data[":::size_mapping:::"], indices)
        elif scale_type == "discrete" :
            quantiles = normalize(np.array(labels, dtype=np.float))
        else :
            raise GgplotError("Unknow scale_type: '%s'" % scale_type)

        legend_entry = {
            'column_name': size_col,
            'dict': dict(zip(quantiles, labels)),
            'scale_type': scale_type}
    return data, legend_entry

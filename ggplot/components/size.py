import numpy as np


def assign_sizes(gg):
    # We need to normalize size so that the points aren't really big or
    # really small.
    # TODO: add different types of normalization (log, inverse, etc.)
    if 'size' in gg.aesthetics:
        size_col = gg.aesthetics['size']
        gg.data["size_mapping"] = gg.data[size_col].astype(np.float)
        gg.data["size_mapping"] = 200.0 * \
                (gg.data[size_col] - gg.data[size_col].min() + .15) / \
                (gg.data[size_col].max() - gg.data[size_col].min())
        labels = np.percentile(gg.data[size_col], [5, 25, 50, 75, 95])
        quantiles = np.percentile(gg.data["size_mapping"], [5, 25, 50, 75, 95])
        gg.legend["size"] = dict(zip(quantiles, labels))
    return gg

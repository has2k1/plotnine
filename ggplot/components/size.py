import numpy as np


def assign_sizes(data, aes, gg):
    """Assigns size to the given data based on the aes and adds the right legend

    Parameters
    ----------
    data : DataFrame
        dataframe which should have shapes assigned to
    aes : aesthetic
        mapping, including a mapping from shapes to variable
    gg : ggplot
        object, which holds information and gets a legend assigned

    Returns
    -------
    data : DataFrame
        the changed dataframe
    """
    # We need to normalize size so that the points aren't really big or
    # really small.
    # TODO: add different types of normalization (log, inverse, etc.)
    if 'size' in aes:
        size_col = aes['size']
        data["size_mapping"] = data[size_col].astype(np.float)
        data["size_mapping"] = 200.0 * \
                                  (data[size_col] - data[size_col].min() + .15) / \
                                  (data[size_col].max() - data[size_col].min())
        labels = np.percentile(data[size_col], [5, 25, 50, 75, 95])
        quantiles = np.percentile(data["size_mapping"], [5, 25, 50, 75, 95])
        gg.add_to_legend("size", dict(zip(quantiles, labels)))
    return data

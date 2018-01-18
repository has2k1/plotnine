from copy import deepcopy

__all__ = ['layer_data']


def layer_data(p, i=0):
    """
    Return layer information used to draw the plot

    Parameters
    ----------
    p : ggplot
        ggplot object
    i : int
        Layer number

    Returns
    -------
    out : dataframe
        Layer information
    """
    p = deepcopy(p)
    p._build()
    return p.layers.data[i]

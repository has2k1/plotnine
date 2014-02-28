from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import numpy as np
import six

LINESTYLES = [
    '-',  #solid
    '--', #dashed
    '-.', #dash-dot
    ':',  #dotted
    '.',  #point
    '|',  #vline
    '_',  #hline
]

LINESTYLES = [
    'solid',
    'dashed',
    'dashdot',
    'dotted'
]


def line_gen():
    while True:
        for line in LINESTYLES:
            yield line


def assign_linestyles(data, aes, gg):
    """
    Assigns line styles to the given data based on the aes and adds the right 
    legend.

    Parameters
    ----------
    data : DataFrame
        dataframe which should have shapes assigned to
    aes : aesthetic
        mapping, including a mapping from line style to variable
    gg : ggplot object, which holds information and gets a legend assigned

    Returns
    -------
    data : DataFrame
        the changed dataframe
    """

    if 'linestyle' in aes:
        linestyle_col = aes['linestyle']
        possible_linestyles = np.unique(data[linestyle_col])
        linestyle = line_gen()
        linestyle_mapping = dict((value, six.next(linestyle)) for value in possible_linestyles)
        data['linestyle_mapping'] = data[linestyle_col].apply(lambda x: linestyle_mapping[x])
        gg.add_to_legend('linestyle', dict((v, k) for k, v in linestyle_mapping.items()))

    return data

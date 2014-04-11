from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import numpy as np
import six

# Matplolib is not consistent. Sometimes it does not
# accept abbreviations
# LINETYPES = [
#     '-',  #solid
#     '--', #dashed
#     '-.', #dash-dot
#     ':',  #dotted
#     '.',  #point
#     '|',  #vline
#     '_',  #hline
# ]

LINETYPES = [
    'solid',
    'dashed',
    'dashdot',
    'dotted'
]


def line_gen():
    while True:
        for line in LINETYPES:
            yield line


def assign_linetypes(data, aes):
    """
    Assigns line types to the given data based on the aes and adds the right
    legend.

    Parameters
    ----------
    data : DataFrame
        dataframe which should have shapes assigned to
    aes : aesthetic
        mapping, including a mapping from line type to variable

    Returns
    -------
    data : DataFrame
        the changed dataframe
    legend_entry : dict
        An entry into the legend dictionary.
        Documented in `components.legend`
    """

    legend_entry = dict()
    if 'linetype' in aes:
        linetype_col = aes['linetype']
        possible_linetypes = np.unique(data[linetype_col])
        linetype = line_gen()
        linetype_mapping = dict((value, six.next(linetype)) for value in possible_linetypes)
        data[':::linetype_mapping:::'] = data[linetype_col].apply(
            lambda x: linetype_mapping[x])

        legend_entry = {
            'column_name': linetype_col,
            'dict': dict((v, k) for k, v in linetype_mapping.items()),
            'scale_type': "discrete"}
    return data, legend_entry

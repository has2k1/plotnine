from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import six
from .legend import get_labels

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
        linetype = line_gen()
        labels, scale_type, indices = get_labels(data, linetype_col, "discrete")
        linetype_mapping = dict((value, six.next(linetype)) for value in labels)
        data[':::linetype_mapping:::'] = data[linetype_col].apply(
            lambda x: linetype_mapping[x])

        legend_entry = {
            'column_name': linetype_col,
            'dict': dict((v, k) for k, v in linetype_mapping.items()),
            'scale_type': "discrete"}
    return data, legend_entry

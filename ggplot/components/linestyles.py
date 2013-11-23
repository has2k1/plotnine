import sys
import numpy as np

LINESTYLES = [
    '-',    #solid
    '--',   #dashed
    '-.',   #dash-dot
    ':',    #dotted
    '.',    #point
    '|',    #vline
    '_',    #hline
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

def assign_linestyles(gg):
    if 'linestyle' in gg.aesthetics:
        linestyle_col = gg.aesthetics['linestyle']
        possible_linestyles = np.unique(gg.data[linestyle_col])
        linestyle = line_gen()
        if sys.hexversion > 0x03000000:
            linestyle_mapping = {value: linestyle.__next__() for value in possible_linestyles}
        else:
            linestyle_mapping = {value: linestyle.next() for value in possible_linestyles}
        #mapping['marker'] = mapping['linestyle'].replace(linestyle_mapping)
        gg.data['linestyle_mapping'] = gg.data[linestyle_col].apply(lambda x: linestyle_mapping[x])
        gg.legend['linestyle'] = { v: k for k, v in linestyle_mapping.items() }

    return gg

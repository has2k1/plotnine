

LINESTYLES = [
    "-",    #solid
    "--",   #dashed
    "-.",   #dash-dot
    ":",    #dotted
    ".",    #point
    "|",    #vline
    "_",    #hline
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

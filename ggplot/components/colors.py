

COLORS = [
    "black",
	"red",
	"green",
	"blue",
	"orange",
	"cyan",
	"white"
]

COLORS = [
    "#000000",
    "#E69F00", 
    "#56B4E9", 
    "#009E73", 
    "#F0E442", 
    "#0072B2", 
    "#D55E00",
    "#CC79A7"
]

def color_gen():
	while True:
		for color in COLORS:
			yield color

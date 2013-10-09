
SHAPES = [
    'o',#circle
    '^',#triangle up
    'D',#diamond
    'v',#triangle down
    '+',#plus
    'x',#x
    's',#square
    '*',#star
    'p',#pentagon
    '*'#octagon
]

def shape_gen():
    while True:
        for shape in SHAPES:
            yield shape


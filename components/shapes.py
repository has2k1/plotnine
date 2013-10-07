
SHAPES = [
    '.',
    'v',
    '^',
    '<',
    '>',
    '1',
    'o',
    '2', 
    '3',
    '4',
    '8', 
    's',
    'p', 
    '*'
]

def shape_gen():
    while True:
        for shape in SHAPES:
            yield shape


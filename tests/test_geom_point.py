import pandas as pd

from plotnine import ggplot, aes, geom_point, theme, guides


def test_aesthetics():
    df = pd.DataFrame({
            'a': range(5),
            'b': 2,
            'c': 3,
            'd': 4,
            'e': 5,
            'f': 6,
            'g': 7,
            'h': 8,
            'i': 9
        })

    p = (ggplot(df, aes(y='a')) +
         geom_point(aes(x='b')) +
         geom_point(aes(x='c', size='a')) +
         geom_point(aes(x='d', alpha='a'),
                    size=10, show_legend=False) +
         geom_point(aes(x='e', shape='factor(a)'),
                    size=10, show_legend=False) +
         geom_point(aes(x='f', color='factor(a)'),
                    size=10, show_legend=False) +
         geom_point(aes(x='g', fill='a'), stroke=0,
                    size=10, show_legend=False) +
         geom_point(aes(x='h', stroke='a'), fill='white',
                    color='green', size=10) +
         geom_point(aes(x='i', shape='factor(a)'),
                    fill='brown', stroke=2, size=10, show_legend=False) +
         theme(subplots_adjust={'right': 0.85}))

    assert p == 'aesthetics'


def test_no_fill():
    df = pd.DataFrame({'x': range(5), 'y': range(5)})

    p = (ggplot(df, aes('x', 'y'))
         + geom_point(color='red', fill=None, size=5, stroke=1.5)
         + geom_point(aes(y='y+1'),
                      color='blue', fill='none', size=5, stroke=1.5)
         + geom_point(aes(y='y+2'),
                      color='green', fill='', size=5, stroke=1.5)
         + geom_point(aes(y='y+3'),
                      color='yellow', fill='gray', size=5, stroke=1.5))

    assert p == 'no_fill'


class TestColorFillonUnfilledShape:
    df = pd.DataFrame({
        'x': range(6),
        'y': range(6),
        'z': list('aabbcc')
    })
    p = (ggplot(df, aes('x', 'y'))
         + geom_point(shape='3', size=10, stroke=3)
         + guides(fill=False)
         + theme(subplots_adjust={'right': 0.85})
         )

    # Color  Fill  Result
    # No     No    Black
    # No     Yes   Black
    # Yes    No    Color
    # Yes    Yes   Color

    def test_no_mapping(self):
        assert self.p == 'no_mapping'

    def test_fill_only_mapping(self):
        p = self.p + aes(fill='x')
        # Same as above
        assert p == 'no_mapping'

    def test_color_only_mapping(self):
        p = self.p + aes(color='z')
        assert p == 'color_only_mapping'

    def test_color_fill_mapping(self):
        p = self.p + aes(color='z', fill='x')
        # Same as above
        assert p == 'color_only_mapping'

from plotnine import ggplot, aes, geom_blank
from plotnine.data import mtcars


def test_blank():
    gg = ggplot(mtcars, aes(x='wt', y='mpg'))
    gg = gg + geom_blank()
    assert gg == 'blank'

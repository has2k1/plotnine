from plotnine import aes, geom_point, ggplot, stat_hull, theme
from plotnine.data import mtcars

_theme = theme(subplots_adjust={'right': 0.85})


def test_hull():
    p = (ggplot(mtcars)
         + aes('wt', 'mpg', color='factor(cyl)')
         + geom_point()
         + stat_hull(size=1)
         )

    assert p + _theme == 'hull'

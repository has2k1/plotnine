from __future__ import absolute_import, division, print_function

from plotnine import ggplot, aes, geom_blank
from plotnine.data import mtcars


def test_blank():
    gg = ggplot(aes(x='wt', y='mpg'), data=mtcars)
    gg = gg + geom_blank()
    assert gg == 'blank'

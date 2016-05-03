from __future__ import absolute_import, division, print_function

from .. import ggplot, aes, geom_blank
from ..data import mtcars
from .tools import assert_ggplot_equal, cleanup


@cleanup
def test_blank():
    gg = ggplot(aes(x='wt', y='mpg'), data=mtcars)
    gg = gg + geom_blank()
    assert_ggplot_equal(gg, 'blank')

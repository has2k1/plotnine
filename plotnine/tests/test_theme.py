import os

import six
from plotnine import ggplot, aes, geom_point, labs, facet_grid
from plotnine import (theme, theme_538, theme_bw, theme_classic,
                      theme_dark, theme_gray, theme_light,
                      theme_linedraw, theme_matplotlib, theme_minimal,
                      theme_seaborn, theme_void, theme_xkcd)
from plotnine import element_line, element_blank
from plotnine.data import mtcars

_theme = theme(subplots_adjust={'right': 0.80})


def test_add_complete_complete():
    theme1 = theme_gray()
    theme2 = theme_matplotlib()
    theme3 = theme1 + theme2
    assert theme3 == theme2


def test_add_complete_partial():
    theme1 = theme_gray()
    theme2 = theme1 + theme(axis_line_x=element_line())
    assert theme2 != theme1
    assert theme2.themeables != theme1.themeables
    assert theme2.rcParams == theme1.rcParams

    # specific difference
    for name in theme2.themeables:
        if name == 'axis_line_x':
            assert theme2.themeables[name] != theme1.themeables[name]
        else:
            assert theme2.themeables[name] == theme1.themeables[name]


def test_add_partial_complete():
    theme1 = theme(axis_line_x=element_line())
    theme2 = theme_gray()
    theme3 = theme1 + theme2
    assert theme3 == theme2


def test_add_empty_theme_element():
    # An empty theme element does not alter the theme
    theme1 = theme_gray() + theme(axis_line_x=element_line(color='red'))
    theme2 = theme1 + theme(axis_line_x=element_line())
    assert theme1 == theme2


l1 = element_line(color='red', size=1, linewidth=1, linetype='solid')
l2 = element_line(color='blue', size=2, linewidth=2)
l3 = element_line(color='blue', size=2, linewidth=2, linetype='solid')
blank = element_blank()


def test_add_element_heirarchy():
    # parent themeable modifies child themeable
    theme1 = theme_gray() + theme(axis_line_x=l1)  # child
    theme2 = theme1 + theme(axis_line=l2)          # parent
    theme3 = theme1 + theme(axis_line_x=l3)        # child, for comparison
    assert theme2.themeables['axis_line_x'] == \
        theme3.themeables['axis_line_x']

    theme1 = theme_gray() + theme(axis_line_x=l1)  # child
    theme2 = theme1 + theme(line=l2)               # grand-parent
    theme3 = theme1 + theme(axis_line_x=l3)        # child, for comparison
    assert theme2.themeables['axis_line_x'] == \
        theme3.themeables['axis_line_x']

    # child themeable does not affect parent
    theme1 = theme_gray() + theme(axis_line=l1)    # parent
    theme2 = theme1 + theme(axis_line_x=l2)        # child
    theme3 = theme1 + theme(axis_line=l3)          # parent, for comparison
    assert theme3.themeables['axis_line'] != \
        theme2.themeables['axis_line']


def test_add_element_blank():
    # Adding onto a blanked themeable
    theme1 = theme_gray() + theme(axis_line_x=l1)  # not blank
    theme2 = theme1 + theme(axis_line_x=blank)     # blank
    theme3 = theme2 + theme(axis_line_x=l3)        # not blank
    theme4 = theme_gray() + theme(axis_line_x=l3)  # for comparison
    assert theme3 != theme1
    assert theme3 != theme2
    assert theme3 == theme4  # blanking cleans the slate

    # When a themeable is blanked, the apply method
    # is replaced with the blank method.
    th2 = theme2.themeables['axis_line_x']
    th3 = theme3.themeables['axis_line_x']
    assert th2.apply.__name__ == 'blank'
    assert th3.apply.__name__ == 'apply'


class TestThemes(object):
    g = (ggplot(mtcars, aes(x='wt', y='mpg', color='factor(gear)'))
         + geom_point()
         + facet_grid('vs ~ am'))

    def test_theme_538(self):
        p = self.g + labs(title='Theme 538') + theme_538()

        assert p + _theme == 'theme_538'

    def test_theme_bw(self):
        p = self.g + labs(title='Theme BW') + theme_bw()

        assert p + _theme == 'theme_bw'

    def test_theme_classic(self):
        p = self.g + labs(title='Theme Classic') + theme_classic()

        assert p + _theme == 'theme_classic'

    def test_theme_dark(self):
        p = self.g + labs(title='Theme Dark') + theme_dark()

        assert p + _theme == 'theme_dark'

    def test_theme_gray(self):
        p = self.g + labs(title='Theme Gray') + theme_gray()

        assert p + _theme == 'theme_gray'

    def test_theme_light(self):
        p = self.g + labs(title='Theme Light') + theme_light()

        assert p + _theme == 'theme_light'

    def test_theme_linedraw(self):
        p = self.g + labs(title='Theme Linedraw') + theme_linedraw()

        if six.PY2:
            # Small displacement in title
            assert p + _theme == ('theme_linedraw', {'tol': 8})
        else:
            assert p + _theme == 'theme_linedraw'

    def test_theme_matplotlib(self):
        p = self.g + labs(title='Theme Matplotlib') + theme_matplotlib()

        assert p + _theme == 'theme_matplotlib'

    def test_theme_minimal(self):
        p = self.g + labs(title='Theme Minimal') + theme_minimal()

        assert p + _theme == 'theme_minimal'

    def test_theme_seaborn(self):
        p = self.g + labs(title='Theme Seaborn') + theme_seaborn()

        assert p + _theme == 'theme_seaborn'

    def test_theme_void(self):
        p = self.g + labs(title='Theme Void') + theme_void()

        assert p + _theme == 'theme_void'

    def test_theme_xkcd(self):
        p = self.g + labs(title='Theme Xkcd') + theme_xkcd()

        if os.environ.get('TRAVIS'):
            # Travis does not have the fonts, we still check
            # to catch any other errors
            assert p + _theme != 'theme_gray'
        else:
            assert p + _theme == 'theme_xkcd'

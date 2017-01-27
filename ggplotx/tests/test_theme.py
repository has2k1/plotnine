from ggplotx import theme, theme_gray, theme_matplotlib
from ggplotx import element_line, element_blank


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

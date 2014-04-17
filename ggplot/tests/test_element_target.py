from nose.tools import assert_equal, assert_true

from ggplot.themes.element_target import *


def test_element_target1():
    txt = text()
    y = axis_text_y()
    assert_true(len(txt.__class__.__mro__) > len(y.__class__.__mro__))


def test_element_target2():
    txt = text()
    x = axis_text_x()
    y = axis_text_y()
    targets = [y, x, txt]
    assert_equal(sorted_element_targets(targets), [txt, y, x])


def test_element_target3():
    txt1 = text()
    txt2 = text()
    x1 = axis_text_x()
    x2 = axis_text_x()
    y1 = axis_text_y()
    targets = sorted_element_targets([txt1, x1, y1, txt2, x2])
    assert_equal(targets, [txt1, txt2, x1, y1, x2])


def test_element_target4():
    x = axis_text_x()
    y = axis_text_y()
    assert_equal(len(x.__class__.__mro__), len(y.__class__.__mro__))


def test_element_target5():
    txt1 = text()
    txt2 = text()
    x1 = axis_text_x()
    x2 = axis_text_x()
    y1 = axis_text_y()
    targets = unique_element_targets(sorted_element_targets([txt1, x1, y1, txt2, x2]))
    assert_equal(targets, [txt2, y1, x2])

def test_element_target6():
    txt1 = text()
    txt2 = text()
    x1 = axis_text_x()
    x2 = axis_text_x()
    y1 = axis_text_y()
    targets = unique_element_targets(sorted_element_targets([txt1, x1, y1, txt2, x2]))
    assert_equal(targets, [txt2, y1, x2])

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import six
from six.moves import xrange

from nose.tools import assert_equal, assert_true, assert_raises, with_setup
from matplotlib.testing.decorators import image_comparison, cleanup
import matplotlib.pyplot as plt

import os

import pandas as pd
import numpy as np

from ggplot import *

# TODO: test some real file content?

def assert_file_exist(filename, msg=None):
    if not msg:
        msg = "File %s does not exist".format(filename)
    assert_true(os.path.exists(filename), msg)

def assert_exist_and_clean(filename, msg=None):
    assert_file_exist(filename, msg=None)
    os.remove(filename)

def assert_same_dims(orig, new, msg=None):
    if msg is None:
        msg = "Different dimensions: {0} -> {1} vs {2}"
    else:
        msg = msg + "({0} -> {1} vs {2})"
    ow, oh = orig
    nw, nh = new
    #print(orig, new)
    assert_true(ow == nw, msg.format("x", ow, nw))
    assert_true(oh == nh, msg.format("y", oh, nh))
    
@cleanup
def test_ggsave_file():
    gg = ggplot(aes(x='wt',y='mpg',label='name'),data=mtcars) + geom_text()
    # we must print the object otherwise it wont show up as a figure to save
    print(gg)
    fn = "filename.png"
    ggsave(fn)
    assert_exist_and_clean(fn)

@cleanup 
def test_ggsave_plot():
    gg = ggplot(aes(x='wt',y='mpg',label='name'),data=mtcars) + geom_text()
    # supplying the ggplot object will work without printing it first!
    ggsave(gg)
    assert_exist_and_clean(str(gg.__hash__())+".pdf")
    
@cleanup 
def test_ggsave_arguments():
    gg = ggplot(aes(x='wt',y='mpg',label='name'),data=mtcars) + geom_text()
    # supplying the ggplot object will work without printing it first!
    fn = "filename.png"
    ggsave(fn, gg)
    assert_exist_and_clean(fn, "both fn and plot")
    ggsave(fn, gg, path=".")
    assert_exist_and_clean(os.path.join(".", fn), "both fn, plot and path")
    ggsave(gg, format="png")
    assert_exist_and_clean(str(gg.__hash__())+".png", "format png")
    # travis setup has not tiff support
    #ggsave(fn, gg, device="tiff")
    #assert_exist_and_clean(fn, "device tiff")
    ggsave(fn, gg)
    assert_exist_and_clean(fn, "both fn and plot")
    orig = plt.gcf().get_size_inches()
    ggsave(fn, gg, scale=2)
    assert_exist_and_clean(fn, "scale = 2")
    assert_same_dims(orig, plt.gcf().get_size_inches(), "size is different after scale")
    # this works as we use float(scale) to convert it
    ggsave(fn, gg, scale="2")
    assert_same_dims(orig, plt.gcf().get_size_inches(), "size is different after str int scale")
    ggsave(fn, gg, width=1)
    assert_exist_and_clean(fn, "width = 1")
    assert_same_dims(orig, plt.gcf().get_size_inches(), "size is different after width")
    ggsave(fn, gg, height=1)
    assert_exist_and_clean(fn, "height = 1")
    assert_same_dims(orig, plt.gcf().get_size_inches(), "size is different after height")
    ggsave(fn, gg, width=1, height=1)
    assert_exist_and_clean(fn, "both height and width")
    assert_same_dims(orig, plt.gcf().get_size_inches(), "size is different after both")
    ggsave(fn, gg, width=1, height=1, units="cm")
    assert_exist_and_clean(fn, "units = cm")
    assert_same_dims(orig, plt.gcf().get_size_inches(), "size is different after units=cm")
    ggsave(fn, gg, dpi=100)
    assert_exist_and_clean(fn, "dpi=100")

@cleanup 
def test_ggsave_big():
    gg = ggplot(aes(x='wt',y='mpg',label='name'),data=mtcars) + geom_text()
    # supplying the ggplot object will work without printing it first!
    fn = "filename.png"
    # draw() needs to be done once to get the sizes of *this* plot and not some default value
    gg.draw()
    orig = plt.gcf().get_size_inches()
    # 26 is the current limit, just go over it to not use too much memory
    ggsave(fn, gg, width=26, height=26, limitsize=False)
    assert_exist_and_clean(fn, "both height and width big")
    assert_same_dims(orig, plt.gcf().get_size_inches(), "size is different after both")
    
@cleanup 
def test_ggsave_exceptions():
    gg = ggplot(aes(x='wt',y='mpg',label='name'),data=mtcars) + geom_text()
    fn = "filename.png"
    # Needs to be done once to get the sizes of *this* plot and not some default
    gg.draw()
    orig = plt.gcf().get_size_inches()
    with assert_raises(Exception):
        ggsave(gg, format="unknown")
    assert_same_dims(orig, plt.gcf().get_size_inches(), "size is different after unknown ending")
    ggsave(fn, gg)
    with assert_raises(Exception):
        ggsave(fn, gg, scale="x")
    assert_same_dims(orig, plt.gcf().get_size_inches(), "size is different after unknown scale")
    with assert_raises(Exception):
        ggsave(fn, gg, width=300)
    assert_same_dims(orig, plt.gcf().get_size_inches(), "size is different after too big width")
    with assert_raises(Exception):
        ggsave(fn, gg, height=300)
    assert_same_dims(orig, plt.gcf().get_size_inches(), "size is different after too big height")
    with assert_raises(Exception):
        ggsave(fn, gg, width=1, heigth=1, units="xxx")
    assert_same_dims(orig, plt.gcf().get_size_inches(), "size is different after unknown units")
    with assert_raises(Exception):
        ggsave(fn, gg, dpi="xxx")
    assert_same_dims(orig, plt.gcf().get_size_inches(), "size is different after unknown dpi")

@cleanup 
def test_ggsave_close_plot():
    gg = ggplot(aes(x='wt',y='mpg',label='name'),data=mtcars) + geom_text()
    fn = "filename.png"
    ggsave(fn, gg)
    assert_exist_and_clean(fn, "exist")
    assert_true(plt.get_fignums() == [], "ggsave did not close the plot")
    

def test_aes_mixed_args():
    result = aes("weight", "hp", color="qsec")
    expected = {"x": "weight", "y": "hp", "color": "qsec"}
    assert_equal(result,expected)

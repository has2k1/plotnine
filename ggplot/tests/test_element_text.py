from nose.tools import assert_equal, assert_true

from ggplot.tests import image_comparison, cleanup
from ggplot import *


gg = ggplot(aes(x='date', y='beef'), data=meat) + \
    geom_point(color='lightblue') + \
    stat_smooth(span=.15, color='black', se=True) + \
    xlab("Date") + \
    ylab("Head of Cattle Slaughtered")

@image_comparison(["all_text"], extensions=["png"], tol=0)
def test_element_text1():
    # Text element_target properties that can be configured with rcParams.
    print(gg + theme(text=element_text(family="serif", face="bold.italic",
                                       size=20, color="red", angle=45)))

@image_comparison(["axis_text"], extensions=["png"], tol=0)
def test_element_text2():
    # Text element_target properties that can be configured with rcParams.
    print(gg +
          theme(text=element_text(family="serif", face="bold.italic",
                                  size=20, color="red")) +
          theme(axis_text=element_text(color="green", angle=45)))

@image_comparison(["axis_title"], extensions=["png"], tol=0)
def test_element_text3():
    # Text element_target properties that can be configured with rcParams.
    print (gg +
           theme(text=element_text(family="serif", face="bold.italic",
                                   size=20, color="red")) +
           theme(axis_title=element_text(color="purple")))

@image_comparison(["axis_title_text"], extensions=["png"], tol=0)
def test_element_text4():
    # Text element_target properties that can be configured with rcParams.
    print(gg +
          theme(text=element_text(family="serif", face="bold.italic",
                                  size=20, color="red")) +
          theme(axis_text_y=element_text(color="green")) +
          theme(axis_title=element_text(color="blue")))

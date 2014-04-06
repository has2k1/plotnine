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

# based on examples from http://docs.ggplot2.org/current/theme.html
gg = ggplot(aes(x='mpg', y='wt'), data=mtcars) + geom_point()


@image_comparison(["plot_title"], extensions=["png"], tol=0)
def test_element_text5():
    # approximation of example from ggplot2 theme page. Real example
    # uses element_text(size=rel(2))
    l = labs(title="Vehicle Weight-Gas Milage Relationship")
    print(gg + l + theme(plot_title=element_text(size=50, color="blue")))


@image_comparison(["legend_title"], extensions=["png"], tol=0)
def no_test_element_text5():
    # legend is not showing, so this doesn't realy test anything
    gg = ggplot(aes(x='mpg', y='wt', colour='factor(cyl)'),
                data=mtcars) + geom_point()
    print(gg + theme(legend_title=element_text(color="blue")))

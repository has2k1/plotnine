from nose.tools import assert_equal, assert_true

from ggplot.tests import image_comparison, cleanup
from ggplot import *

from numpy import linspace
from pandas import DataFrame

df = DataFrame({"blahblahblah": linspace(999, 1111, 9),
                "yadayadayada": linspace(999, 1111, 9)})
simple_gg = ggplot(aes(x="blahblahblah", y="yadayadayada"), data=df) + geom_line()

    
@image_comparison(["all_text"], extensions=["png"], tol=10)
def test_element_text1():
    print(simple_gg + theme(text=element_text(family="serif", face="bold.italic",
                                       size=50, color="red", angle=45)))

@image_comparison(["axis_text"], extensions=["png"], tol=10)
def test_element_text2():
    print(simple_gg +
          theme(text=element_text(family="serif", face="bold.italic",
                                  size=50, color="red")) +
          theme(axis_text=element_text(color="green", angle=45)))

@image_comparison(["axis_title"], extensions=["png"], tol=10)
def test_element_text3():
    print (simple_gg +
           theme(text=element_text(family="serif", face="bold.italic",
                                   color="red")) +
           theme(axis_title=element_text(color="purple", size=70)))

@image_comparison(["axis_title_text"], extensions=["png"], tol=10)
def test_element_text4():
    print(simple_gg +
          theme(text=element_text(family="serif", face="bold.italic",
                                  color="red")) +
          theme(axis_text_y=element_text(color="green", size=50)) +
          theme(axis_title=element_text(color="blue", size=50)))

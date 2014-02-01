from __future__ import print_function, unicode_literals

import unittest
from ggplot import *

class TestScaleColorBrewer(unittest.TestCase):

    def test_scale_color_brewer(self):
        gghist = ggplot(meat, aes(x='veal')) + geom_histogram()
        p = ggplot(aes(x='carat', y='price', colour='clarity'), data=diamonds)
        p = p + geom_point() + scale_colour_brewer()
        self.assertTrue(type(p) == ggplot)
        print(p)

if __name__ == '__main__':
    unittest.main()

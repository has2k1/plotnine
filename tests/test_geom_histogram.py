from __future__ import print_function, unicode_literals

import unittest
from ggplot import *

class TestGeomHistogram(unittest.TestCase):

    def test_geom_histogram(self):
        gghist = ggplot(meat, aes(x='veal')) + geom_histogram()
        self.assertTrue(type(gghist) == ggplot)
        print(gghist)

    def test_binwidth(self):
        gghist = ggplot(meat, aes(x='veal')) + geom_histogram(binwidth=10)
        print gghist

if __name__ == '__main__':
    unittest.main()

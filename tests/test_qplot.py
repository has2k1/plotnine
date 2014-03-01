from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import unittest
from ggplot import *

class TestQPlot(unittest.TestCase):

    def test_geom_histogram(self):
        gghist = qplot('veal', data=meat, geom='hist')
        self.assertTrue(type(gghist) == ggplot)
        print(gghist)

if __name__ == '__main__':
    unittest.main()

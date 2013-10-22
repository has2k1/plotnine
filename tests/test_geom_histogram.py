import unittest
from ggplot import *

class TestGeomHistogram(unittest.TestCase):

    def test_geom_histogram(self):
        gghist = ggplot(meat, aes(x='veal', y='beef')) + geom_histogram()
        self.assertTrue(type(gghist) == ggplot)
        print gghist

if __name__ == '__main__':
    unittest.main()

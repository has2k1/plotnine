from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import unittest
from ggplot import *

class TestQPlot(unittest.TestCase):

    def test_qplot_auto_point(self):
        gg = qplot('date', 'veal', data=meat)
        self.assertTrue(type(gg.geoms[0])==geom_point)

    def test_qplot_auto_hist(self):
        gg = qplot('veal', data=meat)
        self.assertTrue(type(gg.geoms[0])==geom_histogram)

    def test_qplot_auto_bar(self):
        gg = qplot('cut', data=diamonds)
        self.assertTrue(type(gg.geoms[0])==geom_bar)

    def test_qplot_point(self):
        gg = qplot('date', 'veal', data=meat, geom='point')
        self.assertTrue(type(gg.geoms[0])==geom_point)

    def test_qplot_line(self):
        gg = qplot('date', 'veal', data=meat, geom='line')
        self.assertTrue(type(gg.geoms[0])==geom_line)
    
    def test_qplot_bar(self):
        gg = qplot('cut', data=diamonds, geom='bar')
        self.assertTrue(type(gg.geoms[0])==geom_bar)

    def test_geom_histogram(self):
        gghist = qplot('veal', data=meat, geom='hist')
        self.assertTrue(type(gghist) == ggplot)

    def test_scale_x_log10(self):
        gg = qplot('beef', data=meat, geom='hist', log='x')
        self.assertEqual(gg.scale_x_log, 10)

    def test_scale_y_log10(self):
        gg = qplot('beef', data=meat, geom='hist', log='y')
        self.assertEqual(gg.scale_y_log, 10)

    def test_scale_xy_log10(self):
        gg = qplot('beef', data=meat, geom='hist', log='xy')
        self.assertEqual(gg.scale_x_log, 10)
        self.assertEqual(gg.scale_y_log, 10)

if __name__ == '__main__':
    unittest.main()

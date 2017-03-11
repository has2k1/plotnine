from __future__ import absolute_import, division, print_function
import os
from copy import copy

import matplotlib.pyplot as plt
import pytest

from plotnine import ggplot, aes, geom_text, ggsave
from plotnine.data import mtcars
from plotnine.exceptions import PlotnineError

p = (ggplot(aes(x='wt', y='mpg', label='name'), data=mtcars)
     + geom_text())

# filename = 'filename.png'


def sequential_filenames():
    """
    Generate filenames for the tests
    """
    for i in range(100):
        yield 'filename-{}.png'.format(i)


filename_gen = sequential_filenames()


# TODO: test some real file content?
def assert_file_exist(filename, msg=None):
    if not msg:
        msg = "File {} does not exist".format(filename)
    assert os.path.exists(filename), msg


def assert_exist_and_clean(filename, msg=None):
    assert_file_exist(filename, msg=None)
    os.remove(filename)


class TestArguments(object):
    def test_default_filename(self):
        ggsave(p)
        tokens = ('ggsave-', str(abs(p.__hash__())), '.pdf')
        fn = ''.join(tokens)
        assert_exist_and_clean(fn, "default filename")

    def test_filename_plot(self):
        fn = next(filename_gen)
        ggsave(fn, p)
        assert_exist_and_clean(fn, "filename and plot")

    def test_save_method(self):
        fn = next(filename_gen)
        g = copy(p)
        g.save(fn)
        assert_exist_and_clean(fn, "save method")

    def test_filename_plot_path(self):
        fn = next(filename_gen)
        ggsave(fn, p, path='.')
        assert_exist_and_clean(fn, "fn, plot and path")

    def test_format_png(self):
        ggsave(p, format='png')
        tokens = ('ggsave-', str(abs(p.__hash__())), '.png')
        fn = ''.join(tokens)
        assert_exist_and_clean(fn, "format png")

    def test_dpi(self):
        fn = next(filename_gen)
        ggsave(fn, p, dpi=100)
        assert_exist_and_clean(fn, "dpi = 100")

    def test_ggsave_big(self):
        fn = next(filename_gen)
        # supplying the ggplot object will work without
        # printing it first! 26 is the current limit, just go
        # over it to not use too much memory
        ggsave(fn, p, width=26, height=26,
               limitsize=False)
        assert_exist_and_clean(fn, "big height and width")


class TestExceptions(object):
    def test_unknown_format(self):
        with pytest.raises(PlotnineError):
            ggsave(p, format='unknown')

    def test_bad_scale(self):
        with pytest.raises(Exception):
            ggsave(p, scale='x')

    def test_large_width(self):
        with pytest.raises(PlotnineError):
            ggsave(p, width=300)

    def test_large_height(self):
        with pytest.raises(PlotnineError):
            ggsave(p, height=300)

    def test_bad_units(self):
        with pytest.raises(Exception):
            ggsave(p, width=1, heigth=1, units='xxx')

    def test_bad_dpi(self):
        with pytest.raises(Exception):
            ggsave(p,  dpi='xxx')


def test_ggsave_close_plot():
    fn = next(filename_gen)
    ggsave(fn, p)
    assert_exist_and_clean(fn, "exist")
    assert plt.get_fignums() == [], "ggsave did not close the plot"

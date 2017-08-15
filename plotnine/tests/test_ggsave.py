from __future__ import absolute_import, division, print_function
import os

import matplotlib.pyplot as plt
import pytest
import six

from plotnine import ggplot, aes, geom_text, ggsave
from plotnine.data import mtcars
from plotnine.exceptions import PlotnineError

p = (ggplot(aes(x='wt', y='mpg', label='name'), data=mtcars)
     + geom_text())


def sequential_filenames():
    """
    Generate filenames for the tests
    """
    for i in range(100):
        yield 'filename-{}.png'.format(i)


filename_gen = sequential_filenames()


def assert_file_exist(filename, msg=None):
    if not msg:
        msg = "File {} does not exist".format(filename)
    assert os.path.exists(filename), msg


def assert_exist_and_clean(filename, msg=None):
    assert_file_exist(filename, msg=None)
    os.remove(filename)


class TestArguments(object):
    def test_default_filename(self):
        p.save()
        fn = p._save_filename('pdf')
        assert_exist_and_clean(fn, "default filename")

    @pytest.mark.skipif(six.PY2,
                        reason="pesky string complications in py2")
    def test_save_method(self):
        fn = next(filename_gen)
        with pytest.warns(UserWarning) as record:
            p.save(fn)

        assert_exist_and_clean(fn, "save method")

        res = ('saving' in str(item.message).lower()
               for item in record)
        assert any(res)

        res = ('filename' in str(item.message).lower()
               for item in record)
        assert any(res)

        # verbose
        fn = next(filename_gen)
        with pytest.warns(None) as record:
            p.save(fn, verbose=False)
        assert_exist_and_clean(fn, "save method")

        res = ('saving' in str(item.message).lower()
               for item in record)
        assert not any(res)

        res = ('filename' in str(item.message).lower()
               for item in record)
        assert not any(res)

    def test_filename_plot_path(self):
        fn = next(filename_gen)
        p.save(fn, path='.')
        assert_exist_and_clean(fn, "fn, plot and path")

    def test_format_png(self):
        p.save(format='png')
        fn = p._save_filename('png')
        assert_exist_and_clean(fn, "format png")

    def test_dpi(self):
        fn = next(filename_gen)
        p.save(fn, dpi=100)
        assert_exist_and_clean(fn, "dpi = 100")

    def test_ggsave(self):
        ggsave(p)
        fn = p._save_filename('pdf')
        assert_exist_and_clean(fn, "default filename")

    def test_save_big(self):
        fn = next(filename_gen)
        # supplying the ggplot object will work without
        # printing it first! 26 is the current limit, just go
        # over it to not use too much memory
        p.save(fn, width=26, height=26, limitsize=False)
        assert_exist_and_clean(fn, "big height and width")


class TestExceptions(object):
    def test_unknown_format(self):
        with pytest.raises(Exception):
            p.save(format='unknown')

    def test_width_only(self):
        with pytest.raises(PlotnineError):
            p.save(width=11)

    def test_height_only(self):
        with pytest.raises(PlotnineError):
            p.save(height=8)

    def test_large_width(self):
        with pytest.raises(PlotnineError):
            p.save(width=300, height=8)

    def test_large_height(self):
        with pytest.raises(PlotnineError):
            p.save(widhth=11, height=300)

    def test_bad_units(self):
        with pytest.raises(Exception):
            p.save(width=1, heigth=1, units='xxx')


# This should be the last function in the file since it can catch
# "leakages" due to the tests in this test module.
def test_ggsave_closes_plot():
    assert plt.get_fignums() == [], "There are unsaved test plots"
    fn = next(filename_gen)
    p.save(fn)
    assert_exist_and_clean(fn, "exist")
    assert plt.get_fignums() == [], "ggplot.save did not close the plot"

import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import pytest

from plotnine import (
    aes,
    facet_wrap,
    geom_point,
    geom_text,
    ggplot,
    ggsave,
    theme_xkcd,
)
from plotnine.data import mtcars
from plotnine.exceptions import PlotnineError, PlotnineWarning

p = ggplot(mtcars, aes(x="wt", y="mpg", label="name")) + geom_text()


def sequential_filenames():
    """
    Generate filenames for the tests
    """
    for i in range(100):
        yield Path(f"filename-{i}.png")


filename_gen = sequential_filenames()


def assert_exist_and_clean(filename, msg=None):
    if not msg:
        msg = f"File {filename} does not exist"
    assert filename.exists(), msg
    filename.unlink()


class TestArguments:
    def test_default_filename(self):
        p.save(verbose=False)
        fn = p._save_filename("pdf")
        assert_exist_and_clean(fn, "default filename")

    def test_save_method(self):
        fn = next(filename_gen)
        with pytest.warns(PlotnineWarning) as record:
            p.save(fn)

        assert_exist_and_clean(fn, "save method")

        res = ("saving" in str(item.message).lower() for item in record)
        assert any(res)

        res = ("filename" in str(item.message).lower() for item in record)
        assert any(res)

        # verbose
        fn = next(filename_gen)
        with warnings.catch_warnings(record=True) as record:
            p.save(fn, verbose=False)
            assert_exist_and_clean(fn, "save method")
            assert not record, "Issued an unexpected warning"

    def test_filename_plot_path(self):
        fn = next(filename_gen)
        p.save(fn, path=".", verbose=False)
        assert_exist_and_clean(fn, "fn, plot and path")

    def test_format_png(self):
        p.save(format="png", verbose=False)
        fn = p._save_filename("png")
        assert_exist_and_clean(fn, "format png")

    def test_dpi(self):
        fn = next(filename_gen)
        p.save(fn, dpi=100, verbose=False)
        assert_exist_and_clean(fn, "dpi = 100")

    def test_ggsave(self):
        ggsave(p, verbose=False)
        fn = p._save_filename("pdf")
        assert_exist_and_clean(fn, "default filename")

    def test_save_big(self):
        fn = next(filename_gen)
        # supplying the ggplot object will work without
        # printing it first! 26 is the current limit, just go
        # over it to not use too much memory
        p.save(fn, width=26, height=26, limitsize=False, verbose=False)
        assert_exist_and_clean(fn, "big height and width")

    def test_dpi_theme_xkcd(self):
        fn1 = next(filename_gen)
        fn2 = next(filename_gen)

        data = pd.DataFrame({"x": range(4), "y": range(4), "b": list("aabb")})

        p = (
            ggplot(data)
            + geom_point(aes("x", "y"))
            + facet_wrap("b")
            + theme_xkcd()
        )
        p.save(fn1, verbose=False)
        assert_exist_and_clean(fn1, "Saving with theme_xkcd and dpi (1)")

        p.save(fn2, dpi=72, verbose=False)
        assert_exist_and_clean(fn2, "Saving with theme_xkcd and dpi (2)")


class TestExceptions:
    def test_unknown_format(self):
        with pytest.raises(Exception):
            p.save(format="unknown", verbose=False)

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
            p.save(width=1, heigth=1, units="xxx")


# This should be the last function in the file since it can catch
# "leakages" due to the tests in this test module.
def test_ggsave_closes_plot():
    assert plt.get_fignums() == [], "There are unsaved test plots"
    fn = next(filename_gen)
    p.save(fn, verbose=False)
    assert_exist_and_clean(fn, "exist")
    assert plt.get_fignums() == [], "ggplot.save did not close the plot"

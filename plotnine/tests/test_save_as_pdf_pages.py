import os

import matplotlib.pyplot as plt
import pytest

from plotnine import ggplot, aes, geom_text, ggtitle, theme
from plotnine.data import mtcars
from plotnine.ggplot import save_as_pdf_pages
from plotnine.exceptions import PlotnineError, PlotnineWarning


def p(N=3):
    """Return *N* distinct plot objects."""
    template = (
        ggplot(aes(x='wt', y='mpg', label='name'), data=mtcars) +
        geom_text()
        )
    for i in range(1, N+1):
        yield template + ggtitle('%d of %d' % (i, N))


def sequential_filenames():
    """
    Generate filenames for the tests
    """
    for i in range(100):
        yield f'filename-{i}.pdf'


filename_gen = sequential_filenames()


def assert_file_exist(filename, msg=None):
    if not msg:
        msg = f"File {filename} does not exist"
    assert os.path.exists(filename), msg


def assert_exist_and_clean(filename, msg=None):
    assert_file_exist(filename, msg=None)
    os.remove(filename)


class TestArguments:
    def test_default_filename(self):
        plots = list(p())
        save_as_pdf_pages(plots, verbose=False)
        fn = plots[0]._save_filename('pdf')
        assert_exist_and_clean(fn, "default filename")

    def test_save_method(self):
        fn = next(filename_gen)
        with pytest.warns(UserWarning) as record:
            save_as_pdf_pages(p(), fn)

        assert_exist_and_clean(fn, "save method")

        res = ('filename' in str(item.message).lower()
               for item in record)
        assert any(res)

        # verbose
        fn = next(filename_gen)
        with pytest.warns(None) as record:
            save_as_pdf_pages(p(), fn, verbose=False)
        assert_exist_and_clean(fn, "save method")

        res = ('filename' in str(item.message).lower()
               for item in record)
        assert not any(res)

    def test_filename_plot_path(self):
        fn = next(filename_gen)
        with pytest.warns(PlotnineWarning):
            save_as_pdf_pages(p(), fn, path='.')
        assert_exist_and_clean(fn, "fn, plot and path")

    @pytest.mark.skip("Results of this test can only be confirmed by"
                      "inspecting the generated PDF.")
    def test_height_width(self):
        plots = []
        for i, plot in enumerate(p()):
            plots.append(plot + theme(figure_size=(8+i, 6+i)))
        fn = next(filename_gen)
        with pytest.warns(PlotnineWarning):
            save_as_pdf_pages(plots, fn)
        # assert False, "Check %s" % fn  # Uncomment to check


class TestExceptions:
    def test_plot_exception(self):
        # Force an error in drawing
        fn = next(filename_gen)
        plots = list(p())
        plots[0] += aes(color='unknown')
        with pytest.raises(PlotnineError):
            save_as_pdf_pages(plots, fn, verbose=False)

        assert_exist_and_clean(fn, "Plot exception")


# This should be the last function in the file since it can catch
# "leakages" due to the tests in this test module.
def test_save_as_pdf_pages_closes_plots():
    assert plt.get_fignums() == [], "There are unsaved test plots"
    fn = next(filename_gen)
    with pytest.warns(PlotnineWarning):
        save_as_pdf_pages(p(), fn)
    assert_exist_and_clean(fn, "exist")
    assert plt.get_fignums() == [], "ggplot.save did not close the plot"

from tempfile import NamedTemporaryFile

from plotnine import aes, geom_point, ggplot
from plotnine.composition import Compose
from plotnine.data import mtcars
from plotnine.session import last_plot, reset_last_plot


def test_last_plot_initially_none():
    reset_last_plot()
    assert last_plot() is None


def test_last_plot_after_draw():
    reset_last_plot()
    p = ggplot(mtcars, aes("wt", "mpg")) + geom_point()
    p.draw()
    assert last_plot() is not None
    assert isinstance(last_plot(), ggplot)


def test_last_plot_after_save(tmp_path):
    reset_last_plot()
    p = ggplot(mtcars, aes("wt", "mpg")) + geom_point()

    with NamedTemporaryFile(suffix=".png") as tmp_file:
        p.save(tmp_file.name, verbose=False)

    result = last_plot()
    assert result is not None
    # save() deepcopies, so last_plot won't be the same object
    assert isinstance(result, ggplot)


def test_last_plot_tracks_compose():
    reset_last_plot()
    p1 = ggplot(mtcars, aes("wt", "mpg")) + geom_point()
    p2 = ggplot(mtcars, aes("hp", "mpg")) + geom_point()
    compose = p1 | p2
    compose.draw()
    result = last_plot()
    assert result is not None
    assert isinstance(result, Compose)

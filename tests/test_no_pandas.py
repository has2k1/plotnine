"""
plotnine works with polars and without pandas

The plots are drawn in a separate process in which pandas cannot be
imported.
"""

import subprocess
import sys
import textwrap

import pytest

pytest.importorskip("polars")

BLOCK_PANDAS = textwrap.dedent(
    """
    import sys

    class BlockPandas:
        def find_spec(self, name, path=None, target=None):
            if name == "pandas" or name.startswith("pandas."):
                raise ModuleNotFoundError("pandas is blocked")

    sys.meta_path.insert(0, BlockPandas())
    """
)


def run_without_pandas(code: str) -> subprocess.CompletedProcess:
    code = BLOCK_PANDAS + textwrap.dedent(code)
    return subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True
    )


def _mizani_needs_pandas() -> bool:
    return run_without_pandas("import mizani.bounds").returncode != 0


pytestmark = pytest.mark.skipif(
    _mizani_needs_pandas(),
    reason="The installed version of mizani requires pandas",
)


def test_import_does_not_import_pandas():
    result = run_without_pandas(
        """
        import plotnine
        import plotnine.data
        assert "pandas" not in sys.modules
        assert type(plotnine.data.mpg).__module__.startswith("polars")
        """
    )
    assert result.returncode == 0, result.stderr


PLOTS = {
    "points": """
        ggplot(mpg, aes("displ", "hwy", color="factor(cyl)"))
        + geom_point()
        + labs(title="title")
    """,
    "expressions": """
        ggplot(mpg, aes(nw.col("displ") * 2, "np.log(hwy)"))
        + geom_point(aes(size="cty"))
        + geom_text(aes(label="model"), data=mpg.head(5))
    """,
    "histogram": """
        ggplot(mpg, aes("hwy", fill="drv"))
        + geom_histogram(bins=10)
        + facet_wrap("year")
    """,
    "bars": """
        ggplot(diamonds, aes("cut", fill="clarity"))
        + geom_bar(position="dodge")
        + coord_flip()
    """,
    "boxplot": """
        ggplot(mpg, aes("class", "hwy"))
        + geom_boxplot(notch=True)
        + geom_jitter(width=0.1, random_state=1)
    """,
    "lines": """
        ggplot(economics, aes("date", "unemploy"))
        + geom_line()
        + geom_area(alpha=0.3)
        + scale_x_datetime(date_breaks="10 years")
    """,
    "facet_grid": """
        ggplot(mpg, aes("displ", "hwy"))
        + geom_point()
        + facet_grid("drv", "cyl", margins=True)
    """,
    "tiles": """
        ggplot(faithfuld, aes("waiting", "eruptions", fill="density"))
        + geom_tile()
        + scale_fill_distiller(palette="Blues")
    """,
    "contours": """
        ggplot(faithfuld, aes("waiting", "eruptions", z="density"))
        + geom_contour_filled()
    """,
    "summary": """
        ggplot(mpg, aes("class", "hwy"))
        + stat_summary(fun_data="mean_cl_boot", random_state=1)
        + stat_summary(fun_y=np.median, geom="point", color="red")
    """,
    "annotate": """
        ggplot(mpg, aes("displ", "hwy"))
        + geom_point()
        + annotate("rect", xmin=2, xmax=3, ymin=20, ymax=30, alpha=0.2)
        + geom_hline(yintercept=25)
        + geom_abline(slope=1, intercept=10)
        + annotate("text", x=I(0.5), y=I(0.9), label="literal")
    """,
    "count": """
        ggplot(mpg, aes("cty", "hwy"))
        + geom_count()
        + stat_ellipse()
        + scale_size_area()
    """,
    "polar": """
        ggplot(mpg, aes("factor(cyl)", fill="drv"))
        + geom_bar()
        + coord_radial()
    """,
    "empty": """
        ggplot() + geom_blank() + xlim(0, 1)
    """,
    "density": """
        ggplot(mpg, aes("hwy", fill="drv"))
        + geom_density(alpha=0.5)
        + geom_density(kernel="epanechnikov", bounds=(10, 50))
    """,
    "violin": """
        ggplot(mpg, aes("drv", "hwy"))
        + geom_violin(draw_quantiles=[0.25, 0.5, 0.75])
        + geom_sina(random_state=1)
    """,
    "beeswarm": """
        ggplot(mpg, aes("drv", "hwy")) + geom_beeswarm()
    """,
    "smooth": """
        ggplot(mpg, aes("displ", "hwy"))
        + geom_point()
        + geom_smooth(method="lm")
        + geom_smooth(method="mavg", method_args={"window": 10})
    """,
    "smooth_glm": """
        ggplot(diamonds, aes("carat", "price")) + geom_smooth()
    """,
    "density_2d": """
        ggplot(faithfuld.head(400), aes("waiting", "eruptions"))
        + geom_density_2d()
        + geom_pointdensity()
    """,
    "ecdf_qq": """
        ggplot(mpg, aes(sample="hwy"))
        + stat_ecdf(aes(x="hwy"), inherit_aes=False)
        + geom_qq()
        + geom_qq_line()
    """,
}


@pytest.mark.parametrize("name", PLOTS)
def test_plot(name):
    result = run_without_pandas(
        f"""
        from io import BytesIO

        import narwhals as nw
        import numpy as np

        from plotnine import *
        from plotnine.data import diamonds, economics, faithfuld, mpg

        p = ({PLOTS[name].strip()})
        p.save(BytesIO(), format="png", verbose=False)
        assert "pandas" not in sys.modules
        """
    )
    assert result.returncode == 0, result.stderr


def test_statsmodels_method_has_a_helpful_error():
    result = run_without_pandas(
        """
        from io import BytesIO

        from plotnine import *
        from plotnine.data import mpg
        from plotnine.exceptions import PlotnineError

        p = ggplot(mpg, aes("displ", "hwy")) + geom_smooth(method="rlm")
        try:
            p.save(BytesIO(), format="png", verbose=False)
        except PlotnineError as err:
            assert "requires statsmodels" in str(err)
        else:
            raise AssertionError("Expected an error")
        """
    )
    assert result.returncode == 0, result.stderr

import pandas as pd
import pytest

from plotnine import (
    ggplot,
    aes,
    geom_jitter,
    geom_vline,
    geom_hline,
    annotation_stripes,
    scale_shape_discrete,
    scale_x_continuous,
    guide_legend,
    coord_flip,
)
from plotnine.data import mtcars

n = 4
df = pd.DataFrame({"x": range(n), "y": range(n)})


def test_annotation_stripes_basic():
    pdf = mtcars.assign(gear=pd.Categorical(mtcars.gear),
                        am=pd.Categorical(mtcars.am))
    p = (
        ggplot(pdf)
        + annotation_stripes(
            fills=["#AAAAAA", "#FFFFFF", "#7F7FFF"], alpha=0.3
        )
        + geom_jitter(aes("gear", "wt", shape="gear", color="am"),
                      random_state=5)

        + geom_vline(xintercept=0.5, color="black")
        + geom_vline(xintercept=1.5, color="black")
        + geom_vline(xintercept=2.5, color="black")
        + geom_vline(xintercept=3.5, color="black")
        + scale_shape_discrete(guide=guide_legend(order=1))  # work around #229
    )
    assert p == "annotation_stripes_basic"


def test_annotation_stripes_coord_flip():
    pdf = mtcars.assign(gear=pd.Categorical(mtcars.gear),
                        am=pd.Categorical(mtcars.am))
    p = (
        ggplot(pdf)
        + annotation_stripes(
            fills=["#AAAAAA", "#FFFFFF", "#7F7FFF"], alpha=0.3
        )
        + geom_jitter(aes("gear", "wt", shape="gear", color="am"),
                      random_state=5)

        + geom_vline(xintercept=0.5, color="black")
        + geom_vline(xintercept=1.5, color="black")
        + geom_vline(xintercept=2.5, color="black")
        + geom_vline(xintercept=3.5, color="black")
        + scale_shape_discrete(guide=guide_legend(order=1))  # work around #229
        + coord_flip()
    )
    assert p == "annotation_stripes_coord_flip"


def test_invalid_orientation():
    annotation_stripes(direction='horizontal')
    annotation_stripes(direction='vertical')
    with pytest.raises(ValueError):
        annotation_stripes(direction='Vertical')
    with pytest.raises(ValueError):
        annotation_stripes(direction=23)
    with pytest.raises(ValueError):
        annotation_stripes(direction=pd.Series([1, 2, 3]))


def test_annotation_stripes_horizontal():
    pdf = mtcars.assign(gear=pd.Categorical(mtcars.gear),
                        am=pd.Categorical(mtcars.am))
    p = (
        ggplot(pdf)
        + annotation_stripes(
            fills=["#AAAAAA", "#FFFFFF", "#7F7FFF"], alpha=0.3,
            direction='horizontal'
        )
        + geom_jitter(aes("wt", "gear", shape="gear", color="am"),
                      random_state=5)

        + geom_hline(yintercept=0.5, color="black")
        + geom_hline(yintercept=1.5, color="black")
        + geom_hline(yintercept=2.5, color="black")
        + geom_hline(yintercept=3.5, color="black")
        + scale_shape_discrete(guide=guide_legend(order=1))  # work around #229
    )
    assert p == "annotation_stripes_horizontal"


def test_annotation_stripes_horizontal_coord_flip():
    pdf = mtcars.assign(gear=pd.Categorical(mtcars.gear),
                        am=pd.Categorical(mtcars.am))
    p = (
        ggplot(pdf)
        + annotation_stripes(
            fills=["#AAAAAA", "#FFFFFF", "#7F7FFF"], alpha=0.3,
            direction='horizontal'
        )
        + geom_jitter(aes("wt", "gear", shape="gear", color="am"),
                      random_state=5)

        + geom_hline(yintercept=0.5, color="black")
        + geom_hline(yintercept=1.5, color="black")
        + geom_hline(yintercept=2.5, color="black")
        + geom_hline(yintercept=3.5, color="black")
        + scale_shape_discrete(guide=guide_legend(order=1))  # work around #229
        + coord_flip()
    )
    assert p == "annotation_stripes_horizontal_coord_flip"


def test_annotation_stripes_double():
    pdf = mtcars.assign(gear=pd.Categorical(mtcars.gear),
                        am=pd.Categorical(mtcars.am))
    p = (
        ggplot(pdf)
        + annotation_stripes(
            fills=["#0000FF", "#FF0000"], alpha=0.3,
            direction='vertical'
        )
        + annotation_stripes(
            fills=["#AAAAAA", "#FFFFFF"], alpha=0.3,
            direction='horizontal'
        )
        + geom_jitter(aes("gear", "wt", shape="gear", color="am"),
                      random_state=5)
        + scale_shape_discrete(guide=guide_legend(order=1))  # work around #229
    )
    assert p == "annotation_stripes_double"


def test_annotation_stripes_continuous():
    pdf = mtcars.assign(am=pd.Categorical(mtcars.am))
    p = (
        ggplot(pdf)
        + annotation_stripes(
            fills=["red", "green", "blue"], alpha=0.4, size=1,
            linetype="dashed")
        + geom_jitter(aes("gear", "wt", color="am"),
                      random_state=5)

    )

    assert p == "annotation_stripes_continuous"


def test_annotation_stripes_continuous_transformed():
    pdf = mtcars.assign(am=pd.Categorical(mtcars.am))
    p = (
        ggplot(pdf)
        + annotation_stripes(
            fills=["red", "green", "blue"], alpha=0.1
            )
        + geom_jitter(aes("hp", "wt", color="am"),
                      random_state=5)
        + scale_x_continuous(trans='log2')


    )
    assert p == "annotation_stripes_continuous_transformed"

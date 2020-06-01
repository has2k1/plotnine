import numpy as np
import pandas as pd
import pytest

from plotnine import (
    ggplot,
    aes,
    geom_point,
    geom_vline,
    annotation_stripes,
    coord_flip,
)

n = 9
df = pd.DataFrame({
    'x': np.arange(n) % 3 + 1,
    'y': range(n)
})


def test_annotation_stripes():
    p = (ggplot(df)
         + annotation_stripes(fill_range='no')
         + geom_point(aes('factor(x)', 'y'))
         + geom_vline(xintercept=[0.5, 1.5, 2.5, 3.5])
         )

    assert p == 'annotation_stripes'


def test_annotation_stripes_fill_range():
    p = (ggplot(df)
         + annotation_stripes()
         + geom_point(aes('factor(x)', 'y'))
         + geom_vline(xintercept=[0.5, 1.5, 2.5, 3.5])
         )

    assert p == 'annotation_stripes_fill_range'


def test_annotation_stripes_fill_range_cycle():
    p = (ggplot(df)
         + annotation_stripes(fill_range='cycle')
         + geom_point(aes('factor(x)', 'y'))
         + geom_vline(xintercept=[0.5, 1.5, 2.5, 3.5])
         )

    assert p == 'annotation_stripes_fill_range_cycle'


def test_annotation_stripes_coord_flip():
    p = (ggplot(df)
         + annotation_stripes(fill_range='no')
         + geom_point(aes('factor(x)', 'y'))
         + geom_vline(xintercept=[0.5, 1.5, 2.5, 3.5])
         + coord_flip()
         )

    assert p == 'annotation_stripes_coord_flip'


def test_annotation_stripes_continuous_scale():
    p = (ggplot(df)
         + annotation_stripes()
         + geom_point(aes('x', 'y'))
         + geom_vline(xintercept=[0.5, 1.5, 2.5, 3.5])
         )

    assert p == 'annotation_stripes_continuous_scale'


def test_invalid_orientation():
    with pytest.raises(ValueError):
        annotation_stripes(direction='diagonal')


def test_annotation_stripes_fill_direction_extend():
    p = (ggplot(df)
         + annotation_stripes(
             fill=['red', 'blue', 'green'],
             fill_range='no',
             direction='horizontal',
             extend=(.15, 0.85),
             alpha=0.25
         )
         + geom_point(aes('factor(x)', 'factor(y)'))
         )

    assert p == 'annotation_stripes_fill_direction_extend'


def test_annotation_stripes_single_stripe():
    p = (ggplot(df.assign(x=10))
         + annotation_stripes(fill=["#FF0000", "#00FF00"])
         + geom_point(aes('factor(x)', 'y'))
         )

    assert p == 'annotation_stripes_single_stripe'

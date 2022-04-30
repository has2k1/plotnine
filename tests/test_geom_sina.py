import numpy as np
import pandas as pd

from plotnine import ggplot, aes, geom_violin, geom_sina, coord_flip

n = 50
random_state = np.random.RandomState(123)
uni = random_state.normal(5, .25, n)
bi = np.hstack([
    random_state.normal(4, .25, n),
    random_state.normal(6, .25, n)
])
tri = np.hstack([
    random_state.normal(4, .125, n),
    random_state.normal(5, .125, n),
    random_state.normal(6, .125, n)
])

cats = ['uni', 'bi', 'tri']

df = pd.DataFrame({
    'dist': pd.Categorical(
        np.repeat(cats, [len(uni), len(bi), len(tri)]),
        categories=cats
    ),
    'value': np.hstack([uni, bi, tri])
})


def test_scale_area():
    p = (ggplot(df, aes('dist', 'value'))
         + geom_violin(scale='area')
         + geom_sina(scale='area', random_state=123)
         )

    assert p == 'scale_area'


def test_scale_count():
    p = (ggplot(df, aes('dist', 'value'))
         + geom_violin(scale='count')
         + geom_sina(scale='count', random_state=123)
         )

    assert p == 'scale_count'


def test_scale_area_coordflip():
    p = (ggplot(df, aes('dist', 'value'))
         + geom_violin(scale='area')
         + geom_sina(scale='area', random_state=123)
         + coord_flip()
         )

    assert p == 'scale_area+coord_flip'


def test_method_counts():
    p = (ggplot(df, aes('dist', 'value'))
         + geom_violin()
         + geom_sina(method='counts', random_state=123)
         )

    assert p == 'method_counts'

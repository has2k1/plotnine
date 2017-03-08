from __future__ import absolute_import, division, print_function

import pandas as pd

from plotnine import ggplot, aes, geom_dotplot


df = pd.DataFrame({'x': [1, 2, 2, 3, 3, 3, 4, 4, 4, 4]})


def test_dotdensity():
    p = ggplot(df, aes('x')) + geom_dotplot(bins=15)

    assert p == 'dotdensity'


def test_histodot():
    p = (ggplot(df, aes('x'))
         + geom_dotplot(bins=15, method='histodot'))

    assert p == 'histodot'


def test_stackratio():
    p = (ggplot(df, aes('x'))
         + geom_dotplot(bins=15, stackratio=.75))

    assert p == 'stackratio'


def test_binaxis_y():
    p = (ggplot(df, aes('x', 'x'))
         + geom_dotplot(bins=15, binaxis='y'))

    assert p == 'binaxis_y'


def test_stackdir_down():
    p = (ggplot(df, aes('x'))
         + geom_dotplot(bins=15, stackdir='down'))

    assert p == 'stackdir_down'


def test_stackdir_center():
    p = (ggplot(df, aes('x'))
         + geom_dotplot(bins=15, stackdir='center'))

    assert p == 'stackdir_center'


def test_stackdir_centerwhole():
    p = (ggplot(df, aes('x'))
         + geom_dotplot(bins=15, stackdir='centerwhole'))

    assert p == 'stackdir_centerwhole'

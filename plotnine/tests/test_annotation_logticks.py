import pytest
import numpy as np
import pandas as pd
from mizani.transforms import log_trans

from plotnine import (ggplot, aes, geom_point, scale_x_log10,
                      scale_y_log10, annotation_logticks,
                      scale_x_continuous,
                      coord_flip, element_line, theme)
from plotnine.exceptions import PlotnineWarning


df = pd.DataFrame({'x': 10**np.arange(4)})


def test_annotation_logticks():
    # The grid should align with the logticks
    p = (ggplot(df, aes('x', 'x'))
         + annotation_logticks(sides='b', size=.75)
         + geom_point()
         + scale_x_log10()
         + scale_y_log10()
         + theme(
             panel_grid_minor=element_line(color='green'),
             panel_grid_major=element_line(color='red'))
         )

    assert p == 'annotation_logticks'


def test_annotation_logticks_coord_flip():
    p = (ggplot(df, aes('x', 'x'))
         + annotation_logticks(sides='b', size=.75)
         + geom_point()
         + scale_x_log10()
         + scale_y_log10()
         + coord_flip()
         + theme(
             panel_grid_minor=element_line(color='green'),
             panel_grid_major=element_line(color='red'))
         )

    assert p == 'annotation_logticks_coord_flip'


def test_annotation_logticks_base_8():
    base = 8
    df = pd.DataFrame({'x': base**np.arange(4)})
    # The grid should align with the logticks
    p = (ggplot(df, aes('x', 'x'))
         + annotation_logticks(sides='b', size=.75)
         + geom_point()
         + scale_x_continuous(trans=log_trans(base=base))
         + theme(
             panel_grid_minor=element_line(color='green'),
             panel_grid_major=element_line(color='red'))
         )

    assert p == 'annotation_logticks_base_8'


def test_annotation_logticks_base_5():
    base = 5
    df = pd.DataFrame({'x': base**np.arange(4)})
    # The grid should align with the logticks, and the logticks
    # should not have a midpoint
    p = (ggplot(df, aes('x', 'x'))
         + annotation_logticks(sides='b', size=.75)
         + geom_point()
         + scale_x_continuous(trans=log_trans(base=base))
         + theme(
             panel_grid_minor=element_line(color='green'),
             panel_grid_major=element_line(color='red'))
         )

    assert p == 'annotation_logticks_base_5'


def test_wrong_bases():
    # x axis not transformed
    p = (ggplot(df, aes('x', 'x'))
         + annotation_logticks(sides='b', size=.75, base=10)
         + geom_point()
         )

    with pytest.warns(PlotnineWarning):
        p.draw_test()

    # x axis not transform, but ticks requested for a different base
    p = (ggplot(df, aes('x', 'x'))
         + annotation_logticks(sides='b', size=.75, base=10)
         + scale_x_continuous(trans=log_trans(8))
         + geom_point()
         )

    with pytest.warns(PlotnineWarning):
        p.draw_test()

    # x axis is discrete
    df2 = df.assign(discrete=pd.Categorical([str(a) for a in df['x']]))
    p = (ggplot(df2, aes('discrete', 'x'))
         + annotation_logticks(sides='b', size=.75, base=None)
         + geom_point()
         )

    with pytest.warns(PlotnineWarning):
        p.draw_test()

    # y axis is discrete
    df2 = df.assign(discrete=pd.Categorical([str(a) for a in df['x']]))
    p = (ggplot(df2, aes('x', 'discrete'))
         + annotation_logticks(sides='l', size=.75, base=None)
         + geom_point()
         )

    with pytest.warns(PlotnineWarning):
        p.draw_test()

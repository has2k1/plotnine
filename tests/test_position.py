import string

import numpy as np
import pandas as pd
import pytest

from plotnine import (
    aes,
    after_stat,
    geom_bar,
    geom_boxplot,
    geom_col,
    geom_jitter,
    geom_point,
    geom_rect,
    geom_segment,
    geom_text,
    ggplot,
    position_dodge,
    position_dodge2,
    position_jitter,
    position_jitterdodge,
    position_nudge,
    position_stack,
    scale_y_log10,
    stage,
)
from plotnine.exceptions import PlotnineError
from plotnine.positions.position import position

n = 6
m = 10
random_state = np.random.RandomState(1234567890)
data1 = pd.DataFrame({"x": [1, 2, 1, 2], "y": [1, 1, 2, 2]})
data2 = pd.DataFrame(
    {
        "x": np.repeat(range(n + 1), range(n + 1)),
        "z": np.repeat(range(n // 2), range(3, n * 2, 4)),
    }
)
data3 = pd.DataFrame(
    {
        "x": random_state.choice(["A", "B"], n * m),
        "y": random_state.randint(0, 20, n * m),
        "c": random_state.choice([False, False, True, False], n * m),
    }
)
random_state.seed(1234567890)


def test_jitter():
    data1 = pd.DataFrame({"x": [1, 2, 1, 2], "y": [1, 1, 2, 2]})
    p = (
        ggplot(data1, aes("x", "y"))
        + geom_point(size=10)
        + geom_jitter(size=10, color="red", random_state=random_state)
        + geom_jitter(
            size=10,
            color="blue",
            width=0.1,
            height=0.1,
            random_state=random_state,
        )
    )
    assert p == "jitter"

    with pytest.raises(PlotnineError):
        geom_jitter(position=position_jitter(), width=0.1)


def test_nudge():
    p = (
        ggplot(data1, aes("x", "y"))
        + geom_point(size=10)
        + geom_point(size=10, color="red", position=position_nudge(0.25, 0.25))
    )
    assert p == "nudge"


def test_stack():
    p = ggplot(data2, aes("factor(z)")) + geom_bar(
        aes(fill="factor(x)"), position="stack"
    )
    assert p == "stack"


def test_stack_negative():
    data = data1.copy()
    _loc = data.columns.get_loc
    data.iloc[0, _loc("y")] *= -1
    data.iloc[len(data) - 1, _loc("y")] *= -1
    p = (
        ggplot(data)
        + geom_col(aes("factor(x)", "y", fill="factor(y)"), position="stack")
        + geom_text(
            aes("factor(x)", "y", label="y"),
            position=position_stack(vjust=0.5),
        )
    )

    assert p == "stack-negative"


def test_stack_non_linear_scale():
    data = pd.DataFrame(
        {
            "x": "x",
            "value": [0.1, 10, 100, 1000],
            "cat": ["small", "small", "big", "big"],
        }
    )

    p = (
        ggplot(data, aes("x", "value", fill="cat"))
        + geom_col()
        + scale_y_log10()
    )

    with pytest.warns(RuntimeWarning) as rec:
        assert p == "stack-non-linear-scale"
        assert len(rec) == 1


def test_fill():
    p = ggplot(data2, aes("factor(z)")) + geom_bar(
        aes(fill="factor(x)"), position="fill"
    )
    assert p == "fill"


def test_dodge():
    p = ggplot(data2, aes("factor(z)")) + geom_bar(
        aes(fill="factor(x)"), position="dodge"
    )
    assert p == "dodge"


def test_dodge_preserve_single():
    data1 = pd.DataFrame({"x": ["a", "b", "b"], "y": ["a", "a", "b"]})
    p = ggplot(data1, aes("x", fill="y")) + geom_bar(
        position=position_dodge(preserve="single")
    )
    assert p == "dodge_preserve_single"


def test_dodge_preserve_single_text():
    data1 = pd.DataFrame(
        {"x": ["a", "b", "b", "b"], "y": ["a", "a", "b", "b"]}
    )

    d = position_dodge(preserve="single", width=0.9)
    p = (
        ggplot(data1, aes("x", fill="y"))
        + geom_bar(position=d)
        + geom_text(
            aes(y=after_stat("count"), label=after_stat("count")),
            stat="count",
            position=d,
            va="bottom",
        )
    )
    assert p == "dodge_preserve_single_text"


def test_dodge_segment():
    data = pd.DataFrame(
        {
            "x": list("aaaabbbb"),
            "y": [1, 2, 4, 5, 6, 7, 9, 10],
            "g": list("rrssrrss"),
        }
    )
    p = (
        ggplot(data, aes("x", "y"))
        + geom_segment(
            aes(
                x=stage("x", after_stat="x-.45"),
                xend=after_stat("x+.45"),
                yend=after_stat("y"),
            ),
            stat="summary",
            fun_y=np.mean,
        )
        + geom_segment(
            aes(
                x=stage("x", after_stat="x-.45"),
                xend=after_stat("x+.45"),
                yend=after_stat("y"),
                color="g",
            ),
            stat="summary",
            position=position_dodge(width=0.9),
            fun_y=np.mean,
        )
        + geom_point(aes(y="y", color="g"), position=position_dodge(width=0.9))
    )

    assert p == "dodge_segment"


def test_dodge2():
    p = ggplot(data3, aes("x", "y", color="c")) + geom_boxplot(
        position="dodge2", size=2
    )
    assert p == "dodge2"


def test_dodge2_varwidth():
    p = ggplot(data3, aes("x", "y", color="c")) + geom_boxplot(
        position=position_dodge2(preserve="single"), varwidth=True, size=2
    )
    assert p == "dodge2_varwidth"


def test_dodge2_preserve_single_interval():
    n = 3
    data = pd.DataFrame({"x": range(1, n + 1), "y": range(1, n + 1)})

    p = ggplot(
        data, aes(xmin="x-.45", xmax="x+.45", ymin=0, ymax="y")
    ) + geom_rect(position=position_dodge2(preserve="single"))
    assert p == "dodge2_preserve_single_interval"


def test_jitterdodge():
    data = pd.DataFrame(
        {
            "x": np.ones(n * 2),
            "y": np.repeat(np.arange(n), 2),
            "letters": np.repeat(list(string.ascii_lowercase[:n]), 2),
        }
    )
    position = position_jitterdodge(random_state=random_state)

    p = (
        ggplot(data, aes("x", "y", fill="letters"))
        + geom_point(size=10, fill="black")
        + geom_point(size=10, position=position)
    )
    assert p == "jitterdodge"


def test_position_from_geom():
    geom = geom_point(position="jitter")
    assert isinstance(position.from_geom(geom), position_jitter)

    geom = geom_point(position="position_jitter")
    assert isinstance(position.from_geom(geom), position_jitter)

    geom = geom_point(position=position_jitter())
    assert isinstance(position.from_geom(geom), position_jitter)

    geom = geom_point(position=position_jitter)
    assert isinstance(position.from_geom(geom), position_jitter)


def test_dodge_empty_data():
    empty_data = pd.DataFrame({"x": [], "y": []})
    p = (
        ggplot(data1, aes("x", "y"))
        + geom_point()
        + geom_rect(
            empty_data,
            aes(xmin="x", xmax="x+1", ymin="y", ymax="y+1"),
            position="dodge",
        )
    )
    p.draw_test()

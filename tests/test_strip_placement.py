from plotnine import (
    aes,
    facet_grid,
    facet_wrap,
    geom_point,
    ggplot,
    scale_x_continuous,
    scale_y_continuous,
    theme,
    theme_gray,
)
from plotnine.data import mtcars

p = ggplot(mtcars, aes("wt", "mpg")) + geom_point()


def test_strip_placement_themeable_default_and_set():
    assert theme_gray().getp("strip_placement") == "inside"
    assert theme(strip_placement="outside").getp("strip_placement") == (
        "outside"
    )


def test_facet_wrap_top_inside():
    p1 = p + facet_wrap("cyl") + scale_x_continuous(position="top")
    assert p1 == "facet_wrap_top_inside"


def test_facet_wrap_top_outside():
    p1 = (
        p
        + facet_wrap("cyl")
        + scale_x_continuous(position="top")
        + theme(strip_placement="outside")
    )
    assert p1 == "facet_wrap_top_outside"


def test_facet_grid_top_inside():
    p1 = p + facet_grid("am", "cyl") + scale_x_continuous(position="top")
    assert p1 == "facet_grid_top_inside"


def test_facet_grid_top_outside():
    p1 = (
        p
        + facet_grid("am", "cyl")
        + scale_x_continuous(position="top")
        + theme(strip_placement="outside")
    )
    assert p1 == "facet_grid_top_outside"


def test_facet_grid_right_inside():
    p1 = p + facet_grid("am", "cyl") + scale_y_continuous(position="right")
    assert p1 == "facet_grid_right_inside"


def test_facet_grid_right_outside():
    p1 = (
        p
        + facet_grid("am", "cyl")
        + scale_y_continuous(position="right")
        + theme(strip_placement="outside")
    )
    assert p1 == "facet_grid_right_outside"


def test_facet_grid_top_right_inside():
    p1 = (
        p
        + facet_grid("am", "cyl")
        + scale_x_continuous(position="top")
        + scale_y_continuous(position="right")
    )
    assert p1 == "facet_grid_top_right_inside"


def test_facet_grid_top_right_outside():
    p1 = (
        p
        + facet_grid("am", "cyl")
        + scale_x_continuous(position="top")
        + scale_y_continuous(position="right")
        + theme(strip_placement="outside")
    )
    assert p1 == "facet_grid_top_right_outside"


def test_spine_set_position_outward():
    # Pins the private-API contract that _spine_set_position_outward relies
    # on to move a spine without matplotlib's Spine.set_position(), which
    # would call axis.reset_ticks() and drop per-tick theme styling.
    # Verified against matplotlib 3.11; revisit if this test fails after an
    # mpl upgrade.
    from plotnine._mpl.layout_manager._plot_layout_items import (
        _spine_set_position_outward,
    )

    plot = p + facet_wrap("cyl")
    plot.draw_test()
    ax = plot.axs[0]
    spine = ax.spines["top"]

    _spine_set_position_outward(spine, ax.xaxis, 7.0)

    assert spine.get_position() == ("outward", 7.0)
    ticks = (*ax.xaxis.get_major_ticks(), *ax.xaxis.get_minor_ticks())
    assert ticks  # the axis actually has ticks to re-point
    for tick in ticks:
        assert tick.tick2line._transform is spine._transform

"""
Repeat draws must not lose content to stale figure state

A plot or composition that receives a figure from a host (inset) or a
parent composition must not carry anything from the previous figure
across the handover, and a child drawn standalone after its parent drew
must not draw into the parent's closed figure.
"""

from plotnine._utils.yippie import geom as g
from plotnine._utils.yippie import plot
from plotnine.composition import inset_element


class TestInsetRepeatDraw:
    """
    Drawing a host twice must redraw its insets in full

    The inset adopts the host's new figure on every draw, so nothing it
    laid out on the previous figure may survive and swallow content.
    """

    def test_ggplot_inset(self):
        host = plot.white + g.points
        p = host + inset_element(plot.tomato + g.points, 0.5, 0.5, 1, 1)
        p.draw()
        assert p.draw_equals("ggplot_inset_repeat_draw")

    def test_compose_inset(self):
        host = plot.white + g.points
        inset = (plot.tomato + g.points) | (plot.lightblue + g.points)
        p = host + inset_element(inset, 0.4, 0.4, 1, 1)
        p.draw()
        assert p.draw_equals("compose_inset_repeat_draw")


def test_standalone_draw_of_item_after_parent_draw():
    # A composition closes its figure at the end of the draw. An item
    # drawn standalone afterwards must create and own a fresh figure
    # rather than draw into that closed one.
    c = (plot.red + g.points) | (plot.green + g.points)
    c.draw()
    assert c[0].draw_equals("item_after_parent_draw")


def test_standalone_draw_of_sub_composition_after_parent_draw():
    inner = (plot.red + g.points) | (plot.green + g.points)
    c = inner / (plot.blue + g.points)
    c.draw()
    assert inner.draw_equals("sub_composition_after_parent_draw")

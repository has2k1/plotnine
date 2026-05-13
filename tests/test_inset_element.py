import numpy as np
import pytest
from PIL import Image, ImageDraw

from plotnine import (
    element_line,
    element_rect,
    element_text,
    facet_wrap,
    labs,
    theme,
)
from plotnine._utils.yippie import geom as g
from plotnine._utils.yippie import plot
from plotnine.composition import inset_element, plot_annotation


def _smiley() -> np.ndarray:
    """
    Smooth (anti-aliased) smiley on a sky-blue background

    Rendered at 4x supersample with PIL's vector primitives and
    downsampled with LANCZOS for smooth edges. 270w x 300h.
    """
    SUPER = 4
    W, H = 270, 300
    sw, sh = W * SUPER, H * SUPER

    img = Image.new("RGB", (sw, sh), (135, 206, 235))  # sky
    draw = ImageDraw.Draw(img)

    # Face — yellow ellipse with a generous inset from the canvas edge
    pad = sh // 16
    draw.ellipse([pad, pad, sw - pad, sh - pad], fill=(255, 220, 80))

    # Eyes — tall ovals for character
    eye_r = sw // 14
    eye_y = sh * 0.4
    for cx in (sw * 0.34, sw * 0.66):
        draw.ellipse(
            [cx - eye_r, eye_y - eye_r * 1.3, cx + eye_r, eye_y + eye_r * 1.3],
            fill=(30, 30, 30),
        )

    # Rosy cheeks
    cheek_r = sw // 13
    cheek_y = sh * 0.62
    for cx in (sw * 0.16, sw * 0.84):
        draw.ellipse(
            [cx - cheek_r, cheek_y - cheek_r, cx + cheek_r, cheek_y + cheek_r],
            fill=(255, 140, 140),
        )

    # Smile — lower half of an ellipse (U-shape opening upward)
    smile_box = [sw * 0.30, sh * 0.48, sw * 0.70, sh * 0.82]
    draw.arc(smile_box, start=30, end=150, fill=(30, 30, 30), width=sw // 22)
    return np.asarray(img.resize((W, H), Image.LANCZOS))  # pyright: ignore[reportAttributeAccessIssue]


SMILEY_FACE = _smiley()


class TestInsetAlignTo:
    """
    Verify align_to picks the right host region for the inset's bbox
    """

    def setup_method(self):
        # Fresh objects per test — `inset_element + ggplot` mutates the
        # host's `_insets` list, so sharing instances across tests would
        # let earlier tests pollute later ones.
        self.host = (
            plot.wheat + g.cols + labs(title="HOST") + theme(plot_margin=0.02)
        )
        self.inset = plot.mediumvioletred + g.points + theme(plot_margin=0.02)
        self.area = (0.5, 0.5, 1, 1)

    def test_align_to_panel(self):
        p = self.host + inset_element(
            self.inset + labs(title="INSET (panel)"),
            *self.area,
            align_to="panel",
        )
        assert p == "align_to_panel"

    def test_align_to_plot(self):
        p = self.host + inset_element(
            self.inset + labs(title="INSET (plot)"),
            *self.area,
            align_to="plot",
        )
        assert p == "align_to_plot"

    def test_align_to_full(self):
        p = self.host + inset_element(
            self.inset + labs(title="INSET (full)"),
            *self.area,
            align_to="full",
        )
        assert p == "align_to_full"


class TestNestedOnTop:
    """
    on_top toggled on an inset whose host is itself nested in a
    composition that's inset into an outer host
    """

    def setup_method(self):
        self.inner = plot.lightblue + theme(
            panel_background=element_rect(alpha=0.5)
        )
        self.deep = (
            plot.orange
            + labs(footer="Source: Orange")
            + theme(
                plot_footer=element_text(size=8, color="brown", ha="right"),
                plot_footer_line=element_line(color="orange"),
                plot_footer_background=element_rect(fill="orange", alpha=0.3),
            )
        )

    def _build(self, on_top: bool):
        nested = self.inner + inset_element(
            self.deep, 0.1, 0.1, 0.9, 0.9, on_top=on_top
        )
        compose = nested | plot.gray
        return plot.white + inset_element(compose, 0.1, 0.1, 0.9, 0.9)

    def test_nested_on_top_true(self):
        assert self._build(on_top=True) == "nested_on_top_true"

    def test_nested_on_top_false(self):
        assert self._build(on_top=False) == "nested_on_top_false"


class TestQuadrantInsets:
    """
    Fill a host with four plots in a 2x2 grid — either by attaching
    four insets, one per quadrant, or by composing the four plots
    and attaching them as a single inset that spans the host
    """

    def setup_method(self):
        self.host = plot.white
        self.p1 = plot.gray + g.cols
        self.p2 = plot.lightblue + g.points
        self.p3 = plot.wheat + g.areas
        self.p4 = plot.mediumvioletred + g.texts

    def test_quadrants_separate(self):
        p = (
            self.host
            + inset_element(self.p1, 0, 0.5, 0.5, 1)
            + inset_element(self.p2, 0.5, 0.5, 1, 1)
            + inset_element(self.p3, 0, 0, 0.5, 0.5)
            + inset_element(self.p4, 0.5, 0, 1, 0.5)
        )
        assert p == "quadrants_separate"

    def test_quadrants_composed(self):
        cmp = (
            self.p1
            + self.p2
            + self.p3
            + self.p4
            + plot_annotation(
                theme=theme(plot_background=element_rect(color="black"))
            )
        )
        p = self.host + inset_element(cmp, 0, 0, 1, 1)
        assert p == "quadrants_composed"


class TestPropagateTheme:
    """
    `&` and `*` propagate to a host plot and its insets
    """

    def setup_method(self):
        self.host = plot.white + g.cols
        self.inset = plot.gray + g.points
        self.shared = theme(panel_background=element_rect(fill="pink"))

    def test_host_inset_and(self):
        # & themes both the host and the inset.
        p = (
            self.host + inset_element(self.inset, 0.5, 0.5, 1, 1)
        ) & self.shared
        assert p == "host_inset_and"

    def test_host_inset_mul(self):
        # * themes only the host
        p = (
            self.host + inset_element(self.inset, 0.5, 0.5, 1, 1)
        ) * self.shared
        assert p == "host_inset_mul"

    def test_host_compose_inset_and(self):
        # & on a host whose inset is a Compose themes every child of
        # the compose — exercises Compose.__and__ recursion.
        compose = (plot.lightblue + g.points) | (plot.thistle + g.areas)
        p = (
            self.host + inset_element(compose, 0.2, 0.2, 0.8, 0.8)
        ) & self.shared
        assert p == "host_compose_inset_and"

    def test_host_compose_inset_mul(self):
        # * on a host whose inset is a Compose themes only the host
        compose = (plot.lightblue + g.points) | (plot.thistle + g.areas)
        p = (
            self.host + inset_element(compose, 0.2, 0.2, 0.8, 0.8)
        ) * self.shared
        assert p == "host_compose_inset_mul"

    def test_host_nested_inset_and(self):
        # & on a host whose inset is itself a ggplot with insets —
        # the broadcast must reach the innermost ggplot. Exercises
        # `Insets.__and__`'s recursive arm for ggplot-with-insets.
        deep = plot.lightblue + g.points
        middle = plot.white + g.areas + inset_element(deep, 0.5, 0.5, 1, 1)
        p = (
            self.host + inset_element(middle, 0.2, 0.2, 0.8, 0.8)
        ) & self.shared
        assert p == "host_nested_inset_and"

    def test_host_nested_inset_mul(self):
        # * on a host whose inset is itself a ggplot with insets,
        # themes only the host
        deep = plot.lightblue + g.points
        middle = plot.white + g.areas + inset_element(deep, 0.5, 0.5, 1, 1)
        p = (
            self.host + inset_element(middle, 0.2, 0.2, 0.8, 0.8)
        ) * self.shared
        assert p == "host_nested_inset_mul"

    def test_and_non_theme(self):
        # & with a non-theme PlotAddable — host and inset both pick
        # up the geom.
        p = (self.host + inset_element(self.inset, 0.5, 0.5, 1, 1)) & g.texts
        assert p == "and_non_theme"

    def test_and_bare_ggplot_raises(self):
        # On a plot with no insets, `&` is undefined.
        with pytest.raises(TypeError):
            _ = self.host & self.shared

    def test_mul_bare_ggplot_raises(self):
        with pytest.raises(TypeError):
            _ = self.host * self.shared


class TestImageInset:
    """
    Image (ndarray / PIL) renders inside the user's bbox with
    aspect-preservation, anchor placement, themed background, and
    the standalone-render path
    """

    def setup_method(self):
        self.host = plot.white
        self.image = SMILEY_FACE  # ndarray, 270w x 300h
        self.area = (0.5, 0.5, 1, 1)  # top-right quadrant

    def test_aspect_fit_top_right(self):
        # The 9:10 (slightly tall) image in a wider bbox letterboxes
        # left/right; `anchor="top-right"` shifts the image flush to
        # the bbox's right edge. One test exercises aspect-fit and
        # anchor placement together.
        p = self.host + inset_element(
            self.image, *self.area, anchor="top-right"
        )
        assert p == "image_aspect_fit_top_right"

    def test_aspect_fit_bottom(self):
        # A wide image (3:1) in the same bbox (~1.4 aspect)
        # letterboxes top/bottom; `anchor="bottom"` shifts the image
        # flush to the bbox's bottom edge. Exercises the
        # `img_aspect > box_aspect` branch of `_fit_aspect` that the
        # top-right test (image taller than bbox) does not.
        H, W = 30, 90
        wide = np.zeros((H, W, 3), dtype=np.uint8)
        wide[:, : W // 2] = (220, 80, 200)  # left half: magenta
        wide[:, W // 2 :] = (80, 200, 220)  # right half: cyan
        wide[:2, :] = wide[-2:, :] = (30, 30, 30)  # top/bottom border
        wide[:, :2] = wide[:, -2:] = (30, 30, 30)  # left/right border
        bg = theme(
            plot_background=element_rect(fill="whitesmoke", color="black")
        )
        p = self.host + (inset_element(wide, *self.area, anchor="bottom") + bg)
        assert p == "image_aspect_fit_bottom"

    def test_themed_background_wraps_envelope(self):
        # Themed fill + border surround the full user bbox, with the
        # fill visible in the letterbox padding bands and the border
        # tracing the user-specified envelope (not the fitted image).
        bordered = inset_element(self.image, *self.area) + theme(
            plot_background=element_rect(
                fill="lavender", color="purple", size=2
            )
        )
        assert self.host + bordered == "image_themed_bg_wraps"

    def test_ndarray_and_pil_render_identically(self):
        # Same image content as ndarray and PIL.Image must produce
        # identical baselines — pins the input contract through
        # `_image_size` and `np.asarray(self._image)` in
        # `_InsetImage`.
        pil = Image.fromarray(self.image)
        p_arr = self.host + inset_element(self.image, *self.area)
        p_pil = self.host + inset_element(pil, *self.area)
        assert p_arr == "image_basic"
        assert p_pil == "image_basic"

    def test_standalone(self):
        # `inset_element(arr, ...)` renders via the implicit blank
        # ggplot host — the raster equivalent of the standalone
        # ggplot-inset path.
        assert (
            inset_element(self.image, 0.25, 0.25, 0.75, 0.75)
            == "image_standalone"
        )

    def test_invalid_inputs_raise(self):
        # Construction-time validation: bad obj, bad anchor name,
        # bad anchor tuple all raise before any draw.
        with pytest.raises(TypeError, match="ggplot, Compose, PIL image"):
            inset_element("not an image", 0, 0, 1, 1)  # pyright: ignore[reportArgumentType]
        with pytest.raises(ValueError, match="Unknown anchor"):
            inset_element(self.image, 0, 0, 1, 1, anchor="middle")  # pyright: ignore[reportArgumentType]
        with pytest.raises(ValueError, match=r"\[0, 1\]"):
            inset_element(self.image, 0, 0, 1, 1, anchor=(1.5, 0.5))


def test_compose_inset():
    host = plot.white
    p1 = plot.lightblue + g.points
    p2 = plot.gray + g.areas
    inset = (p1 | p2) + plot_annotation(
        theme=theme(plot_background=element_rect(color="black"))
    )
    p = host + inset_element(inset, 0.1, 0.1, 0.9, 0.9)
    assert p == "compose_inset"


def test_inset_attached_to_compose():
    # The inset is attached to the last plot in the composition
    p1 = plot.lightblue
    p2 = plot.lightgray
    p3 = plot.tomato
    cmp = (p1 / p2) + inset_element(p3, 0.5, 0.5, 1, 1)
    assert cmp == "inset_attached_to_compose"


def test_overlapping_insets():
    p1 = plot.gray + g.cols
    p2 = plot.lightblue + g.points
    host = plot.white
    p = (
        host
        + inset_element(p1, 0.1, 0.1, 0.7, 0.7)
        + inset_element(p2, 0.3, 0.3, 0.9, 0.9)
    )
    assert p == "overlapping_insets"


def test_inset_on_facet_host():
    host = plot.white + g.points + facet_wrap("cat")
    p = (
        host
        + inset_element(plot.slateblue, 0, 0.75, 0.25, 1)
        + inset_element(plot.violet, 0.75, 0.75, 1, 1)
        + inset_element(plot.sandybrown, 0.75, 0, 1, 0.25)
        + inset_element(plot.tomato, 0, 0, 0.25, 0.25)
    )
    assert p == "inset_on_facet_host"

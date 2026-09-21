from __future__ import annotations

import gzip
import importlib
from base64 import b64decode
from io import BytesIO
from types import SimpleNamespace
from typing import TYPE_CHECKING, Any, Literal

import pytest
from matplotlib.collections import PolyCollection, QuadMesh
from matplotlib.figure import Figure
from PIL import Image

import plotnine.options as options
from plotnine import (
    aes,
    geom_point,
    ggplot,
    guide_colorbar,
    guides,
    theme,
)
from plotnine.composition import inset_element, plot_annotation, plot_layout
from plotnine.data import mtcars

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def colour_plot() -> ggplot:
    return (
        ggplot(mtcars, aes("wt", "mpg", color="hp"))
        + geom_point()
        + guides(color=guide_colorbar(display="gradient"))
        + theme(figure_size=(3, 2), dpi=72, figure_format="svg")
    )


@pytest.fixture
def saved_figures(monkeypatch: pytest.MonkeyPatch) -> list[Figure]:
    figures = []
    savefig = Figure.savefig

    def save(figure: Figure, *args: Any, **kwargs: Any) -> None:
        figures.append(figure)
        savefig(figure, *args, **kwargs)

    monkeypatch.setattr(Figure, "savefig", save)
    return figures


def test_filename_extension_overrides_theme(
    colour_plot: ggplot, tmp_path: Path
) -> None:
    filename = tmp_path / "plot.pdf"

    colour_plot.save(filename, verbose=False)

    assert filename.read_bytes().startswith(b"%PDF")


def test_theme_format_adds_extension_to_filename_without_one(
    colour_plot: ggplot, tmp_path: Path
) -> None:
    colour_plot.save(tmp_path / "plot", verbose=False)

    assert b"<svg" in (tmp_path / "plot.svg").read_bytes()


def test_explicit_format_does_not_add_a_filename_extension(
    colour_plot: ggplot, tmp_path: Path
) -> None:
    filename = tmp_path / "plot"

    colour_plot.save(filename, format="pdf", verbose=False)

    assert filename.read_bytes().startswith(b"%PDF")


def test_svgz_filename_writes_compressed_svg(
    colour_plot: ggplot, tmp_path: Path
) -> None:
    filename = tmp_path / "plot.svgz"

    colour_plot.save(filename, verbose=False)

    assert b"<svg" in gzip.decompress(filename.read_bytes())


def test_composition_uses_annotation_figure_format(
    colour_plot: ggplot,
) -> None:
    composition = (colour_plot | colour_plot) + plot_annotation(
        theme=theme(figure_format="pdf")
    )
    destination = BytesIO()

    composition.save(destination)

    assert destination.getvalue().startswith(b"%PDF")


@pytest.mark.parametrize("display", ["gradient", "raster", "rectangles"])
def test_pdf_preserves_colourbar_display(
    colour_plot: ggplot,
    display: Literal["gradient", "raster", "rectangles"],
) -> None:
    """
    Preserve each colourbar display mode in PDF output

    SVG-specific rendering must not affect PDF output or change the display
    mode stored on the source guide.
    """
    p = colour_plot + guides(color=guide_colorbar(display=display))
    view = p.save_helper(BytesIO(), format="pdf", verbose=False)
    assert view.kwargs["format"] == "pdf"
    meshes = view.figure.findobj(QuadMesh)
    if display == "rectangles":
        assert view.figure.findobj(PolyCollection)
        assert not meshes
    else:
        assert len(meshes) == 1
        assert meshes[0].get_rasterized() == (display == "raster")
    assert p.guides.color.display == display


@pytest.mark.parametrize("composed", [False, True])
@pytest.mark.parametrize(
    "filename, format, size",
    [
        ("plot.png", None, (432, 288)),
        ("plot.png", "png", (216, 144)),
    ],
)
def test_retina_save_does_not_change_original_dpi(
    colour_plot: ggplot,
    tmp_path: Path,
    composed: bool,
    filename: str | None,
    format: str | None,
    size: tuple[int, int],
) -> None:
    t = theme(figure_format="retina", figure_size=(3, 2), dpi=72)
    obj = (
        (colour_plot | colour_plot) + plot_annotation(theme=t)
        if composed
        else colour_plot + t
    )
    for _ in range(2):
        destination = tmp_path / filename if filename else BytesIO()
        obj.save(destination, format=format, verbose=False)
        with Image.open(destination) as image:
            assert image.size == size
    assert obj.theme.getp("dpi") == 72
    assert obj.theme.getp("figure_format") == "retina"


def test_unknown_save_format(colour_plot: ggplot) -> None:
    with pytest.raises(ValueError, match="not supported"):
        colour_plot.save(BytesIO(), format="unknown", verbose=False)


@pytest.mark.parametrize("composed", [False, True])
@pytest.mark.parametrize(
    "preference, option, inline, mimetype",
    [
        ("SVG", "png", "jpeg", "image/svg+xml"),
        (None, "svg", "png", "image/svg+xml"),
        (None, None, "jpeg", "image/jpeg"),
        (None, None, None, "image/png"),
        ("retina", "svg", None, "image/png"),
        ("jpg", "png", None, "image/jpeg"),
    ],
)
def test_notebook_format_precedence(
    monkeypatch: pytest.MonkeyPatch,
    composed: bool,
    preference: str | None,
    option: str | None,
    inline: str | None,
    mimetype: str,
) -> None:
    """
    Resolve notebook formats without changing the source theme

    Plots and compositions prefer the theme setting, then the global option,
    then the IPython setting, and default to retina output. Repeated rendering
    must preserve the object's format and DPI settings.
    """
    p = ggplot(mtcars, aes("wt", "mpg")) + geom_point()
    t = theme(figure_format=preference, figure_size=(3, 2), dpi=72)
    obj = (p | p) + plot_annotation(theme=t) if composed else p + t
    monkeypatch.setattr(options, "figure_format", option)
    module = importlib.import_module(
        "plotnine.composition._compose" if composed else "plotnine.ggplot"
    )
    ip = SimpleNamespace(
        config=SimpleNamespace(InlineBackend={"figure_format": inline})
    )
    monkeypatch.setattr(module, "get_ipython", lambda: ip)
    for _ in range(2):
        bundle, metadata = obj._repr_mimebundle_()
        assert set(bundle) == {mimetype}
        if mimetype == "image/svg+xml":
            assert "<svg" in bundle[mimetype]
        else:
            image = Image.open(BytesIO(b64decode(bundle[mimetype])))
            if mimetype == "image/png":
                assert image.size == (432, 288)
                assert metadata[mimetype] == {"width": 216, "height": 144}
            else:
                assert image.format == "JPEG"
    assert obj.theme.getp("figure_format") == preference
    assert obj.theme.getp("dpi") == 72


@pytest.mark.parametrize("collection", ["collect", "keep"])
def test_figure_format_controls_nested_guides_and_insets(
    colour_plot: ggplot,
    saved_figures: list[Figure],
    collection: Literal["collect", "keep"],
) -> None:
    """
    Apply an explicit save format throughout nested compositions

    The requested format controls every guide and inset, whether guides are
    collected or kept with their plots. Saving in different formats must
    preserve all stored format preferences.
    """
    p = colour_plot + guides(
        color=guide_colorbar(theme=theme(figure_format="svg"))
    )
    inset = p + theme(figure_format="png")
    host = p + inset_element(inset, 0.4, 0.4, 1, 1)
    inner = (host | p) + plot_annotation(theme=theme(figure_format="png"))
    obj = (inner / p) + plot_layout(guides=collection)
    obj += plot_annotation(theme=theme(figure_format="svg"))
    leaves = list(obj.iter_plots_all())
    preferences = [leaf.theme.getp("figure_format") for leaf in leaves]
    for format in ("svg", "pdf"):
        obj.save(BytesIO(), format=format)
        figure = saved_figures[-1]
        if format == "svg":
            assert figure.findobj(PolyCollection)
            assert not figure.findobj(QuadMesh)
        else:
            assert len(figure.findobj(QuadMesh)) >= 2
            assert not figure.findobj(PolyCollection)
    assert obj.theme.getp("figure_format") == "svg"
    assert [leaf.theme.getp("figure_format") for leaf in leaves] == preferences
    assert inset.theme.getp("figure_format") == "png"


def test_composition_format_overrides_child_preference(
    colour_plot: ggplot,
) -> None:
    p = colour_plot + guides(
        color=guide_colorbar(theme=theme(figure_format="svg"))
    )
    obj = p | p
    figure = obj.draw()
    assert figure.findobj(QuadMesh)

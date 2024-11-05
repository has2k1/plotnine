from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable, Literal, TypeAlias

    from IPython.core.interactiveshell import InteractiveShell

    FigureFormat: TypeAlias = Literal[
        "png", "retina", "jpeg", "jpg", "svg", "pdf"
    ]


def get_ipython() -> "InteractiveShell":
    """
    Return running IPython instance or None
    """
    try:
        from IPython.core.getipython import get_ipython as _get_ipython
    except ImportError as err:
        raise type(err)("IPython is has not been installed.") from err

    ip = _get_ipython()
    if ip is None:
        raise RuntimeError("Not running in a juptyer session.")

    return ip


def is_inline_backend():
    """
    Return True if the inline_backend is on

    This can only be True if also running in an jupyter/ipython session.
    """
    import matplotlib as mpl

    return "matplotlib_inline.backend_inline" in mpl.get_backend()


def get_display_function(
    format: FigureFormat, figure_size_px: tuple[int, int]
) -> Callable[[bytes], None]:
    """
    Return a function that will display the plot image
    """
    from IPython.display import (
        SVG,
        Image,
        display_jpeg,
        display_pdf,
        display_png,
        display_svg,
    )

    w, h = figure_size_px

    def png(b: bytes):
        display_png(Image(b, format="png", width=w, height=h))

    def retina(b: bytes):
        display_png(Image(b, format="png", retina=True))

    def jpeg(b: bytes):
        display_jpeg(Image(b, format="jpeg", width=w, height=h))

    def svg(b: bytes):
        display_svg(SVG(b))

    def pdf(b: bytes):
        display_pdf(b, raw=True)

    lookup = {
        "png": png,
        "retina": retina,
        "jpeg": jpeg,
        "jpg": jpeg,
        "svg": svg,
        "pdf": pdf,
    }
    return lookup[format]

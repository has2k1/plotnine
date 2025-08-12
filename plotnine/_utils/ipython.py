from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable, Literal, NotRequired, TypeAlias, TypedDict

    from IPython.core.interactiveshell import InteractiveShell

    FigureFormat: TypeAlias = Literal[
        "png", "retina", "jpeg", "jpg", "svg", "pdf"
    ]

    class DisplayMetadata(TypedDict):
        width: NotRequired[int]
        height: NotRequired[int]


def get_ipython() -> "None | InteractiveShell":
    """
    Return running IPython instance or None
    """
    try:
        from IPython.core.getipython import get_ipython as _get_ipython
    except ImportError:
        return None

    return _get_ipython()


def is_inline_backend():
    """
    Return True if the inline_backend is on

    This can only be True if also running in an jupyter/ipython session.
    """
    import matplotlib as mpl

    return "matplotlib_inline.backend_inline" in mpl.get_backend()


def get_display_function() -> Callable[
    [dict[str, bytes], dict[str, DisplayMetadata]], None
]:
    """
    Return a function that will display the plot image
    """
    from IPython.display import display

    def display_func(
        data: dict[str, bytes], metadata: dict[str, DisplayMetadata]
    ) -> None:
        display(data, metadata=metadata, raw=True)

    return display_func


def get_mimebundle(
    b: bytes, format: FigureFormat, figure_size_px: tuple[int, int]
):
    """
    Return a the display MIME bundle from image data

    Parameters
    ----------
    format :
        The figure format
    figure_size_px :
        The figure size in pixels (width, height)
    """

    lookup = {
        "png": "image/png",
        "retina": "image/png",
        "jpeg": "image/jpeg",
        "svg": "image/svg+xml",
        "pdf": "application/pdf",
    }
    mimetype = lookup[format]

    metadata: dict[str, DisplayMetadata] = {}
    w, h = figure_size_px
    if format in ("png", "jpeg"):
        metadata = {mimetype: {"width": w, "height": h}}
    elif format == "retina":
        # `retina=True` in IPython.display.Image just halves width/height
        metadata = {mimetype: {"width": w // 2, "height": h // 2}}

    return {mimetype: b}, metadata

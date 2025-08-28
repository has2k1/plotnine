import os
import sys
from functools import lru_cache


def is_quarto_environment() -> bool:
    """
    Return True if running in quarto
    """
    return "QUARTO_FIG_WIDTH" in os.environ


def set_options_from_quarto():
    """
    Set options from quarto
    """
    from plotnine.options import set_option

    dpi = int(os.environ["QUARTO_FIG_DPI"])
    figure_size = (
        float(os.environ["QUARTO_FIG_WIDTH"]),
        float(os.environ["QUARTO_FIG_HEIGHT"]),
    )
    # quarto verifies the format
    # If is retina, it doubles the original dpi and changes the
    # format to png. Since we cannot tell whether fig-format is
    # png or retina, we assume retina.
    figure_format = os.environ["QUARTO_FIG_FORMAT"]
    if figure_format == "png":
        figure_format = "retina"
        dpi = dpi // 2

    set_option("dpi", dpi)
    set_option("figure_size", figure_size)
    set_option("figure_format", figure_format)


# We do not expect the contents the file stored in the QUARTO_EXECUTE_INFO
# variable to change. We can can cache the output
@lru_cache()
def is_knitr_engine() -> bool:
    """
    Return True if knitr is executing the code
    """

    if filename := os.environ.get("QUARTO_EXECUTE_INFO"):  # Quarto >= 1.8.21
        import json
        from pathlib import Path

        info = json.loads(Path(filename).read_text())
        return info["format"]["execute"]["engine"] == "knitr"
    else:
        # NOTE: Remove this branch some time after quarto 1.9 is released
        return "rpytools" in sys.modules

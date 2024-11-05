import os


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

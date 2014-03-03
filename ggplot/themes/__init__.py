from .theme import theme
from .theme_bw import theme_bw
from .theme_gray import theme_gray
from .theme_xkcd import theme_xkcd
from .theme_matplotlib import theme_matplotlib
from .theme_seaborn import theme_seaborn

__all__ = ["theme_bw","theme_gray","theme_xkcd","theme_matplotlib",
           "theme_seaborn"]
__all__ = [str(u) for u in __all__]

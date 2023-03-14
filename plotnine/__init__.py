from importlib.metadata import PackageNotFoundError, version

from .coords import *
from .facets import *
from .geoms import *
from .ggplot import ggplot, ggsave, save_as_pdf_pages
from .guides import *
from .labels import *
from .mapping import *
from .positions import *
from .qplot import qplot
from .scales import *
from .stats import *
from .themes import *
from .watermark import watermark

try:
    __version__ = version("plotnine")
except PackageNotFoundError:
    # package is not installed
    pass
finally:
    del version
    del PackageNotFoundError


def _get_all_imports():
    """
    Return list of all the imports

    This prevents sub-modules (geoms, stats, utils, ...)
    from being imported into the user namespace by the
    following import statement

        from plotnine import *

    This is because `from Module import Something`
    leads to `Module` itself coming into the namespace!!
    """
    from types import ModuleType

    lst = [
        name
        for name, obj in globals().items()
        if not (name.startswith("_") or isinstance(obj, ModuleType))
    ]
    return lst


__all__ = _get_all_imports()

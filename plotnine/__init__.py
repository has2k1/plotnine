from .qplot import qplot            # noqa: F401
from .ggplot import ggplot, ggsave  # noqa: F401
from .ggplot import save_as_pdf_pages  # noqa: F401
from .watermark import watermark    # noqa: F401
from .aes import *                  # noqa: F401,F403,E261
from .labels import *               # noqa: F401,F403,E261
from .coords import *               # noqa: F401,F403,E261
from .geoms import *                # noqa: F401,F403,E261
from .stats import *                # noqa: F401,F403,E261
from .scales import *               # noqa: F401,F403,E261
from .facets import *               # noqa: F401,F403,E261
from .themes import *               # noqa: F401,F403,E261
from .positions import *            # noqa: F401,F403,E261
from .guides import *               # noqa: F401,F403,E261

from ._version import get_versions

__version__ = get_versions()['version']
del get_versions


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
    import types
    lst = [name for name, obj in globals().items()
           if not (name.startswith('_') or
                   name == 'absolute_import' or
                   isinstance(obj, types.ModuleType))]
    return lst


__all__ = _get_all_imports()

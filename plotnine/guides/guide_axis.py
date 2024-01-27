from .._utils import no_init_mutable
from .guide import guide


class guide_axis(guide):
    """
    Axis
    """

    # Non-Parameter Attributes
    available_aes: set[str] = no_init_mutable({"x", "y"})

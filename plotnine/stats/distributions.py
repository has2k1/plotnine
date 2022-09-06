import scipy.stats as stats

from ..exceptions import PlotnineError


def _hasattrs(obj, attrs):
    return all(hasattr(obj, attr) for attr in attrs)


# Continuous univariate
continuous = {
    k for k in dir(stats)
    if _hasattrs(getattr(stats, k), ('pdf', 'cdf'))
}

# Discrete univariate
discrete = {
    k for k in dir(stats)
    if hasattr(getattr(stats, k), 'pmf')
}

univariate = continuous | discrete


def get(name):
    """
    Get any scipy.stats distribution of a given name
    """
    try:
        return getattr(stats, name)
    except AttributeError:
        raise PlotnineError(
            f"Unknown distribution '{name}'"
        )


def get_continuous_distribution(name):
    """
    Get continuous scipy.stats distribution of a given name
    """
    if name not in continuous:
        msg = "Unknown continuous distribution '{}'"
        raise ValueError(msg.format(name))

    return getattr(stats, name)


def get_univariate(name):
    """
    Get univariate scipy.stats distribution of a given name
    """
    if name not in univariate:
        msg = "Unknown univariate distribution '{}'"
        raise ValueError(msg.format(name))

    return get(name)

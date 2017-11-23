import scipy.stats as stats

from ..exceptions import PlotnineError


def _hasattrs(obj, attrs):
    return all(hasattr(obj, attr) for attr in attrs)


# Continuous univariate
continuous = {k for k in dir(stats)
              if _hasattrs(getattr(stats, k), ('pdf', 'cdf'))}

# Discreate univariate
discrete = {k for k in dir(stats)
            if hasattr(getattr(stats, k), 'pmf')}

univariate = continuous | discrete


def get(name):
    try:
        return getattr(stats, name)
    except AttributeError:
        raise PlotnineError(
            "Unknown distribution '{}'".format(name))


def get_continuous_distribution(name):
    if name not in continuous:
        msg = "Unknown continuous distribution '{}'"
        raise ValueError(msg.format(name))

    return getattr(stats, name)


def get_univariate(name):
    if name not in univariate:
        msg = "Unknown univariate distribution '{}'"
        raise ValueError(msg.format(name))

    return get(name)

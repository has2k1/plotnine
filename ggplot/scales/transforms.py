from __future__ import absolute_import, division, print_function

import re
from types import FunctionType

import six
import numpy as np
import pandas as pd
import scipy.stats as stats
from matplotlib.dates import AutoDateLocator, DateFormatter
from matplotlib.dates import date2num, num2date, YEARLY
from matplotlib.ticker import MaxNLocator, Formatter
from matplotlib.ticker import ScalarFormatter

from ..utils import identity, gg_import
from ..utils.exceptions import GgplotError


__all__ = ['asn_trans', 'atanh_trans', 'boxcox_trans', 'datetime_trans',
           'exp_trans', 'identity_trans', 'log10_trans', 'log1p_trans',
           'log2_trans', 'log_trans', 'probability_trans',
           'reverse_trans', 'sqrt_trans', 'timedelta_trans',
           'trans_new']


# Breaks and Formats
class TimedeltaFormatter(Formatter):

    def __call__(self, x, pos=0):
        return str(pd.Timedelta(x))


class defaultLocator(MaxNLocator):

    def __init__(self, nbins=7, steps=(1, 2, 5, 10)):
        MaxNLocator.__init__(self, nbins=nbins, steps=steps)


class TimedeltaLocator(defaultLocator):

    def tick_values(self, vmin, vmax):
        # The tick locations are pretty bad. There should be
        # a better way, maybe choose seconds, hours, days, ...
        # based vmax - vmin
        vmin, vmax = vmin.value, vmax.value
        ticks = defaultLocator.tick_values(self, vmin, vmax)
        ticks = [pd.Timedelta(int(x)) for x in ticks]
        return np.asarray(ticks)


class DateLocator(AutoDateLocator):

    def __init__(self):
        AutoDateLocator.__init__(self, minticks=5, interval_multiples=True)
        self.intervald[YEARLY] = [5, 50]
        self.create_dummy_axis()

    def tick_values(self, vmin, vmax):
        ticks = AutoDateLocator.tick_values(self, vmin, vmax)
        # For consistency with other locators, return ticks
        # in the same space as the inputs.
        return num2date(ticks)


def trans_new(name, transform, inverse,
              breaks=None, format_=None,
              domain=(-np.inf, np.inf)):
    """
    Create a transformation class object

    This class is used to transform data and also tell the
    x and y axes how to create and label the tick locations.

    Parameters
    ----------
    name : str
        Name of the transformation
    transform : function
        A function (preferrably a `ufunc`) that computes
        the transformation.
    inverse : function
        A function (preferrably a `ufunc`) that computes
        the inverse of the transformation.
    breaks : function
        Function to compute the breaks for this transform.
        If None, then a default good enough for a linear
        domain is used.
    format_ : function
        Function to format the generated breaks.
    domain : array-like
        Domain over which the transformation is valid. It should
        be of length 2.

    Returns
    -------
    out : trans
        Transform class
    """
    trans_name = str('{}_trans'.format(name))

    class klass(object):
        aesthetic = None

        @classmethod
        def breaks(cls, limits):
            """
            Calculate breaks in data space and return them
            in transformed space.

            Expects limits to be in transform space
            """
            # clip the breaks to the domain,
            # e.g. probabilities will be in [0, 1] domain
            vmin = np.max([cls.domain[0], limits[0]])
            vmax = np.min([cls.domain[1], limits[1]])
            return cls._locator.tick_values(vmin, vmax)

        @classmethod
        def format(cls, x):
            # For MPL to play nice
            cls._formatter.create_dummy_axis()
            # For sensible decimal places
            cls._formatter.set_locs([i for i in x if ~np.isnan(i)])
            labels = [cls._formatter(tick) for tick in x]

            # Remove unnecessary decimals
            pattern = re.compile(r'\.0+$')
            for i, label in enumerate(labels):
                match = re.search(pattern, label)
                if match:
                    labels[i] = re.sub(pattern, '', label)

            return labels

        @classmethod
        def minor_breaks(cls, breaks, limits):
            if len(breaks) < 2:
                return np.array([])

            diff = np.diff(breaks)
            step = diff[0]

            # For equidistant breaks we can imagine more invisible
            # breaks at either end and then add minor breaks
            # accordingly
            if all(step == diff):
                breaks = np.hstack([-step+breaks[0],
                                    breaks,
                                    breaks[-1]+step])
                minor = breaks[:-1] + step/2
            else:
                minor = breaks[:-1] + diff/2

            minor = minor.compress(
                (limits[0] <= minor) & (minor <= limits[1]))
            return minor

    klass.__name__ = trans_name
    klass.name = name
    klass.dataspace_is_ordinal = True
    klass.transform = staticmethod(transform)
    klass.inverse = staticmethod(inverse)
    klass.domain = domain

    if breaks is not None:
        klass.breaks = classmethod(breaks)

    if format_ is not None:
        klass.format = classmethod(format)

    klass._locator = defaultLocator()
    klass._formatter = ScalarFormatter(useOffset=False)
    return klass


def log_trans(base=None):
    """
    Create a log transform class for base

    Parameters
    ----------
    base : float
        Base for the logarithm. If None, then
        the natural log is used.
    """
    # transform function
    if base is None:
        name = 'log'
        base = np.exp(1)
        transform = np.log
    elif base == 10:
        name = 'log10'
        transform = np.log10
    elif base == 2:
        name = 'log2'
        transform = np.log2
    else:
        name = 'log{}'.format(base)

        def transform(x):
            return np.log(x)/np.log(base)

    # inverse function
    def inverse(x):
        return base ** x

    return trans_new(name, transform, inverse,
                     domain=(1e-100, np.inf))


def exp_trans(base=None):
    """
    Exponential Transformation

    This is inverse of the log transform.

    Parameters
    ----------
    base : float
        Base of the logarithm
    """
    # default to e
    if base is None:
        name = 'power-e'
        base = np.exp(1)
    else:
        name = 'power-{}'.format(base)

    # transform function
    def transform(x):
        return base ** x

    # inverse function
    def inverse(x):
        return np.log(x)/np.log(base)

    return trans_new(name, transform, inverse)


log10_trans = log_trans(10)
log2_trans = log_trans(2)
log1p_trans = trans_new('log1p', np.log1p, np.expm1)
identity_trans = trans_new('identity', identity, identity)
reverse_trans = trans_new('reverse', np.negative, np.negative)
sqrt_trans = trans_new('sqrt', np.sqrt, np.square, domain=(0, np.inf))
asn_trans = trans_new('asn',
                      lambda x: 2*np.arcsin(np.sqrt(x)),
                      lambda x: np.sin(x/2)**2)
atanh_trans = trans_new('atanh', np.arctanh, np.tanh)


def boxcox_trans(p):
    """
    Boxcox Transformation

    Parameters
    ----------
    p : float
        Power parameter, commonly denoted by
        lower-case lambda in formulae
    """
    if np.abs(p) < 1e-7:
        return log_trans()

    def transform(x):
        return (x**p - 1) / (p * np.sign(x-1))

    def inverse(x):
        return (np.abs(x) * p + np.sign(x)) ** (1 / p)

    return trans_new('pow-{}'.format(p), transform, inverse)


def probability_trans(distribution, *args, **kwargs):
    """
    Probability Transformation

    Parameters
    ----------
    distribution : str
        Name of the distribution
    """
    cdists = {k for k in dir(stats) if hasattr(getattr(stats, k), 'cdf')}
    if distribution not in cdists:
        msg = "Unknown distribution '{}'"
        raise GgplotError(msg.format(distribution))

    def transform(x):
        return getattr(stats, distribution).cdf(x, *args, **kwargs)

    def inverse(x):
        return getattr(stats, distribution).ppf(x, *args, **kwargs)

    return trans_new('prob-{}'.format(distribution),
                     transform, inverse, domain=(0, 1))


logit_trans = probability_trans('logistic')
probit_trans = probability_trans('norm')


def datetime_trans():
    """
    Datetime Transformation
    """
    def transform(x):
        """
        Transform from date to ordinal format
        """
        try:
            x = date2num(x)
        except AttributeError:
            # numpy datetime64
            x = [pd.Timestamp(item) for item in x]
            x = date2num(x)
        return x

    def inverse(x):
        """
        Transform to date from ordinal format
        """
        return num2date(x)

    def _DateFormatter():
        return DateFormatter('%Y-%m-%d')

    _trans = trans_new('datetime', transform, inverse)
    _trans.dataspace_is_ordinal = False
    _trans._locator = DateLocator()
    _trans._formatter = DateFormatter('%Y-%m-%d')
    return _trans


def timedelta_trans():
    """
    Timedelta Transformation
    """
    def transform(x):
        """
        Transform from Timeddelta to ordinal format
        """
        try:
            x = np.array([_x.value for _x in x])
        except TypeError:
            x = x.value
        return x

    def inverse(x):
        """
        Transform to Timedelta from ordinal format
        """
        try:
            x = [pd.Timedelta(int(i)) for i in x]
        except TypeError:
            x = pd.Timedelta(int(x))
        return x

    _trans = trans_new('timedelta', transform, inverse)
    _trans.dataspace_is_ordinal = False
    _trans._locator = TimedeltaLocator()
    _trans._formatter = TimedeltaFormatter()
    return _trans


def gettrans(t):
    """
    Return a trans object

    Parameters
    ----------
    t : string | function | class | object
        name of transformation function

    Returns
    -------
    out : trans
    """
    obj = t
    # Make sure trans object is instantiated
    if isinstance(obj, six.string_types):
        obj = gg_import('{}_trans'.format(obj))()
    if isinstance(obj, FunctionType):
        obj = obj()
    if isinstance(obj, type):
        obj = obj()
    return obj

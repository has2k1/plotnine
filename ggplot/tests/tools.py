from __future__ import absolute_import, division, print_function
import os
import contextlib
import warnings
import inspect
import shutil

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import cbook
from matplotlib.testing.compare import compare_images
from nose.tools import make_decorator, with_setup

__all__ = ['assert_warns', 'assert_no_warnings',
           'assert_ggplot_equal', 'cleanup',
           'ignore_warning']


def ignore_warning(message='', category=UserWarning,
                   module='', append=False):
    """
    Ignore warnings that match the regex in message

    See `warnings.filterwarnings` for full description of
    the arguments
    """
    def wrap(testfunc):
        def wrapped():
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore',
                                        message=message,
                                        category=category,
                                        module=module,
                                        append=append)
                testfunc()
        return make_decorator(testfunc)(wrapped)
    return wrap


class ImagesComparisonFailure(Exception):
    pass


def _assert_same_figure_images(fig, name, test_file, tol=17):
    """Asserts that the figure object produces the right image"""
    if '.png' not in name:
        name = name + '.png'

    basedir = os.path.abspath(os.path.dirname(test_file))
    basename = os.path.basename(test_file)
    subdir = os.path.splitext(basename)[0]

    baseline_dir = os.path.join(basedir, 'baseline_images', subdir)
    result_dir = os.path.abspath(os.path.join('result_images', subdir))

    if not os.path.exists(result_dir):
        cbook.mkdirs(result_dir)

    orig_expected_fname = os.path.join(baseline_dir, name)
    actual_fname = os.path.join(result_dir, name)

    def make_test_fn(fname, purpose):
        base, ext = os.path.splitext(fname)
        return '%s-%s%s' % (base, purpose, ext)

    expected_fname = make_test_fn(actual_fname, 'expected')
    # Save the figure before testing whether the original image
    # actually exists. This make creating new tests much easier,
    # as the result image can afterwards just be copied.
    fig.savefig(actual_fname)
    if os.path.exists(orig_expected_fname):
        shutil.copyfile(orig_expected_fname, expected_fname)
    else:
        raise Exception("Baseline image %s is missing" %
                        orig_expected_fname)
    err = compare_images(expected_fname, actual_fname,
                         tol, in_decorator=True)
    if err:
        msg = ('images not close: {actual:s} vs. {expected:s}'
               ' (RMS {rms:.2f})').format(**err)
        raise ImagesComparisonFailure(msg)
    return err


def assert_ggplot_equal(gg, name, tol=17):
    """
    Return True if ggplot object produces the right image

    Parameters
    ----------
    gg : ggplot
        ggplot object to be plotted
    name : str
        Name of image file (without the extension) to be
        compared against. If the file is not present it
        will be created and placed in the
        `result_images/[test_module]` directory and the
        assertion will fail.
    tol : float
        The RMS threshold above which the test is considered
        failed. Default is 17.

    Return
    ------
    out : bool
        Whether the comparison was similar given the tolerance.

    Note
    ----
    If the assertion false and the result image is correct,
    it should be copied from `result_images/[test_module]/`
    to `ggplot/tests/baseline_images/[test_module]/`.
    """
    # filename of the parent frame
    test_file = inspect.stack()[1][1]
    fig = gg.draw()
    return _assert_same_figure_images(fig, name, test_file, tol=tol)


# This is called from the cleanup decorator
def _setup():
    # The baseline images are created in this locale, so we should use
    # it during all of the tests.
    import locale
    import warnings
    from matplotlib.backends import backend_agg, backend_pdf, backend_svg

    try:
        locale.setlocale(locale.LC_ALL, str('en_US.UTF-8'))
    except locale.Error:
        try:
            locale.setlocale(locale.LC_ALL, str('English_United States.1252'))
        except locale.Error:
            warnings.warn(
                "Could not set locale to English/United States. "
                "Some date-related tests may fail")

    mpl.use('Agg', warn=False)  # use Agg backend for these tests
    if mpl.get_backend().lower() != "agg":
        msg = ("Using a wrong matplotlib backend ({0}), "
               "which will not produce proper images")
        raise Exception(msg.format(mpl.get_backend()))

    # These settings *must* be hardcoded for running the comparison
    # tests
    mpl.rcdefaults()  # Start with all defaults
    mpl.rcParams['text.hinting'] = True
    mpl.rcParams['text.antialiased'] = True
    # mpl.rcParams['text.hinting_factor'] = 8

    # Clear the font caches.  Otherwise, the hinting mode can travel
    # from one test to another.
    backend_agg.RendererAgg._fontd.clear()
    backend_pdf.RendererPdf.truetype_font_cache.clear()
    backend_svg.RendererSVG.fontd.clear()
    # make sure we don't carry over bad plots from former tests
    msg = ("no of open figs: {} -> find the last test with ' "
           "python tests.py -v' and add a '@cleanup' decorator.")
    assert len(plt.get_fignums()) == 0, msg.format(plt.get_fignums())


def cleanup(func):
    """Decorator to add cleanup to the testing function

      @cleanup
      def test_something():
          " ... "

    Note that `@cleanup` is useful *only* for test functions, not for test
    methods or inside of TestCase subclasses.
    """

    def _teardown():
        plt.close('all')
        warnings.resetwarnings()  # reset any warning filters set in tests

    return with_setup(setup=_setup, teardown=_teardown)(func)


# assert_warn
# Credit: numpy
@contextlib.contextmanager
def _assert_warns_context(warning_class, name=None):
    __tracebackhide__ = True  # Hide traceback for py.test
    with warnings.catch_warnings(record=True) as l:
        warnings.simplefilter('always')
        yield
        if not len(l) > 0:
            name_str = " when calling %s" % name if name is not None else ""
            raise AssertionError("No warning raised" + name_str)
        if not l[0].category is warning_class:
            name_str = "%s " % name if name is not None else ""
            raise AssertionError("First warning %sis not a %s (is %s)"
                                 % (name_str, warning_class, l[0]))


def assert_warns(warning_class, *args, **kwargs):
    """
    Fail unless the given callable throws the specified warning.
    A warning of class warning_class should be thrown by the callable when
    invoked with arguments args and keyword arguments kwargs.
    If a different type of warning is thrown, it will not be caught, and the
    test case will be deemed to have suffered an error.
    If called with all arguments other than the warning class omitted, may be
    used as a context manager:
        with assert_warns(SomeWarning):
            do_something()
    The ability to be used as a context manager is new in NumPy v1.11.0.
    .. versionadded:: 1.4.0
    Parameters
    ----------
    warning_class : class
        The class defining the warning that `func` is expected to throw.
    func : callable
        The callable to test.
    \\*args : Arguments
        Arguments passed to `func`.
    \\*\\*kwargs : Kwargs
        Keyword arguments passed to `func`.
    Returns
    -------
    The value returned by `func`.
    """
    if not args:
        return _assert_warns_context(warning_class)

    func = args[0]
    args = args[1:]
    with _assert_warns_context(warning_class, name=func.__name__):
        return func(*args, **kwargs)


@contextlib.contextmanager
def _assert_no_warnings_context(name=None):
    __tracebackhide__ = True  # Hide traceback for py.test
    with warnings.catch_warnings(record=True) as l:
        warnings.simplefilter('always')
        yield
        if len(l) > 0:
            name_str = " when calling %s" % name if name is not None else ""
            raise AssertionError("Got warnings%s: %s" % (name_str, l))


def assert_no_warnings(*args, **kwargs):
    """
    Fail if the given callable produces any warnings.
    If called with all arguments omitted, may be used as a context manager:
        with assert_no_warnings():
            do_something()
    The ability to be used as a context manager is new in NumPy v1.11.0.
    .. versionadded:: 1.7.0
    Parameters
    ----------
    func : callable
        The callable to test.
    \\*args : Arguments
        Arguments passed to `func`.
    \\*\\*kwargs : Kwargs
        Keyword arguments passed to `func`.
    Returns
    -------
    The value returned by `func`.
    """
    if not args:
        return _assert_no_warnings_context()

    func = args[0]
    args = args[1:]
    with _assert_no_warnings_context(name=func.__name__):
        return func(*args, **kwargs)

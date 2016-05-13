from __future__ import absolute_import, division, print_function
import os

import matplotlib as mpl

# Testing framework shamelessly stolen from matplotlib...

# Tests which should be run with 'python tests.py' or via 'must be
# included here.
default_test_modules = [
    'ggplot.tests.test_geom',
    'ggplot.tests.test_geom_abline',
    'ggplot.tests.test_geom_blank',
    'ggplot.tests.test_geom_boxplot',
    'ggplot.tests.test_geom_crossbar',
    'ggplot.tests.test_geom_errorbar_errorbarh',
    'ggplot.tests.test_geom_hline',
    'ggplot.tests.test_geom_linerange_pointrange',
    'ggplot.tests.test_geom_path_line_step',
    'ggplot.tests.test_geom_point',
    'ggplot.tests.test_geom_polygon',
    'ggplot.tests.test_geom_rect_tile',
    'ggplot.tests.test_geom_ribbon_area',
    'ggplot.tests.test_geom_rug',
    'ggplot.tests.test_geom_segment',
    'ggplot.tests.test_geom_spoke',
    'ggplot.tests.test_geom_text_label',
    'ggplot.tests.test_geom_vline',
    'ggplot.tests.test_ggplot_internals',
    'ggplot.tests.test_ggsave',
    'ggplot.tests.test_scale_internals',
    'ggplot.tests.test_stat',
    'ggplot.tests.test_stat_calculate_methods',
    'ggplot.tests.test_utils',

    # 'ggplot.tests.test_stat_summary',
    # 'ggplot.tests.test_basic',
    # 'ggplot.tests.test_readme_examples',
    # 'ggplot.tests.test_geom_rect',
    # 'ggplot.tests.test_qplot',
    # 'ggplot.tests.test_geom_lines',
    # 'ggplot.tests.test_faceting',
    # 'ggplot.tests.test_stat_function',
    # 'ggplot.tests.test_scale_facet_wrap',
    # 'ggplot.tests.test_scale_log',
    # 'ggplot.tests.test_reverse',
    # 'ggplot.tests.test_theme_mpl',
    # 'ggplot.tests.test_legend',
    # 'ggplot.tests.test_element_target',
    # 'ggplot.tests.test_element_text',
    # 'ggplot.tests.test_theme',
    # 'ggplot.tests.test_theme_bw',
    # 'ggplot.tests.test_theme_gray',
    # 'ggplot.tests.test_theme_mpl',
    # 'ggplot.tests.test_theme_seaborn',
]

figsize_orig = mpl.rcParams["figure.figsize"]
_multiprocess_can_split_ = True


def setup_package():
    mpl.rcParams["figure.figsize"] = (11.0, 8.0)


def teardown_package():
    mpl.rcParams["figure.figsize"] = figsize_orig


# Check that the test directories exist
if not os.path.exists(os.path.join(
        os.path.dirname(__file__), 'baseline_images')):
    raise IOError(
        'The baseline image directory does not exist. '
        'This is most likely because the test data is not installed. '
        'You may need to install ggplot from source to get the '
        'test data.')


# This is here to run it like "from ggplot.tests import test; test()"
def test(verbosity=1):
    """run the ggplot test suite"""
    old_backend = mpl.rcParams['backend']
    try:
        mpl.use('agg')
        import nose
        import nose.plugins.builtin
        from matplotlib.testing.noseclasses import KnownFailure
        from nose.plugins.manager import PluginManager
        from nose.plugins import multiprocess

        # store the old values before overriding
        plugins = []
        plugins.append(KnownFailure())
        plugins.extend([plugin() for plugin in nose.plugins.builtin.plugins])

        manager = PluginManager(plugins=plugins)
        config = nose.config.Config(verbosity=verbosity, plugins=manager)

        # Nose doesn't automatically instantiate all of the plugins in the
        # child processes, so we have to provide the multiprocess plugin with
        # a list.
        multiprocess._instantiate_plugins = [KnownFailure]

        success = nose.run(defaultTest=default_test_modules,
                           config=config)
    finally:
        if old_backend.lower() != 'agg':
            mpl.use(old_backend)

    return success
test.__test__ = False  # nose: this function is not a test

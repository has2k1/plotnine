import matplotlib as mpl
    
default_test_modules = [
    'ggplot.tests.test_basic',
    'ggplot.tests.test_reverse',
    'ggplot.tests.test_theme_mpl',
    ]


# Testing framework shamelessly stolen from matplotlib...
# This uses the matplotlib facilities...
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
        plugins.append( KnownFailure() )
        plugins.extend( [plugin() for plugin in nose.plugins.builtin.plugins] )

        manager = PluginManager(plugins=plugins)
        config = nose.config.Config(verbosity=verbosity, plugins=manager)

        # Nose doesn't automatically instantiate all of the plugins in the
        # child processes, so we have to provide the multiprocess plugin with
        # a list.
        multiprocess._instantiate_plugins = [KnownFailure]

        success = nose.run( defaultTest=default_test_modules,
                            config=config,
                            )
    finally:
        if old_backend.lower() != 'agg':
            mpl.use(old_backend)

    return success

test.__test__ = False # nose: this function is not a test

import matplotlib as mpl

def setup():
    mpl.use('Agg', warn=False) # use Agg backend for these tests
    mpl.interactive(False)

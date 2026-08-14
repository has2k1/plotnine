import matplotlib as mpl
from packaging.version import Version

# Matplotlib 3.10 requires numeric line spacing and produces different text
# extents from 3.11. Text elements use this flag to convert `normal`; the test
# suite uses it to require Matplotlib 3.11. Remove the flag and both uses when
# plotnine requires Matplotlib 3.11.
MPL_LT_311 = Version(mpl.__version__) < Version("3.11")

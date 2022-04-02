import sys
from setuptools import setup

# This appears to be necessary so that versioneer works
# Ref: python-versioneer/python-versioneer/issues/193
sys.path.insert(0, ".")  # noqa
import versioneer        # noqa


setup(
    # Move these to setup.cfg or pyproject.toml
    # whenever it is possible to do so
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass()
)

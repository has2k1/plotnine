from distutils.core import setup
from setuptools import find_packages


required = []

setup(
    name="ggplot",
    version="0.1.6",
    author="Greg Lamp",
    author_email="greg@yhathq.com",
    url="https://github.com/yhat/ggplot/",
    license="BSD",
    packages=find_packages(),
    package_dir={"ggplot": "ggplot"},
    package_data={"ggplot": ["data/*.csv"]},
    description="ggplot for python",
    # run pandoc --from=markdown --to=rst --output=README.rst README.md
    long_description=open("README.rst").read(),
    install_requires=required,
)


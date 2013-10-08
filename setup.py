from distutils.core import setup
from setuptools import find_packages


required = []

setup(
    name="ggplot",
    version="0.1.0",
    author="Greg Lamp",
    author_email="greg@yhathq.com",
    url="https://github.com/yhat/ggplot/",
    license=open("LICENSE").read(),
    packages=find_packages(),
    package_dir={"ggplot": "ggplot"},
    package_data={"ggplot": ["data/*.csv"]},
    description="ggplot for python",
    long_description=open("README.md").read(),
    install_requires=required,
)


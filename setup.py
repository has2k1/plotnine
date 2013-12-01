from distutils.core import setup
from setuptools import find_packages
import os


required = ["pandas"]

def get_package_data():
    baseline_images = [
        'tests/baseline_images/%s/*' % x
        for x in os.listdir('ggplot/tests/baseline_images')]

    return {
        'ggplot':
        baseline_images +
        [
            "exampledata/*.csv", 
            "geoms/*.png"
        ]} 

setup(
    name="ggplot",
    version="0.4.0",
    author="Greg Lamp",
    author_email="greg@yhathq.com",
    url="https://github.com/yhat/ggplot/",
    license="BSD",
    packages=find_packages(),
    package_dir={"ggplot": "ggplot"},
    package_data=get_package_data(),
    description="ggplot for python",
    # run pandoc --from=markdown --to=rst --output=README.rst README.md
    long_description=open("README.rst").read(),
    install_requires=required,
)


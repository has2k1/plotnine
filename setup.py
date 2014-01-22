import os
from setuptools import find_packages, setup

def extract_version():
    """
    Extracts version values from the main matplotlib __init__.py and
    returns them as a dictionary.
    """
    with open('ggplot/__init__.py') as fd:
        for line in fd.readlines():
            if (line.startswith('__version__')):
                exec(line.strip())
    return locals()["__version__"]

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
    # Increase the version in ggplot/__init__.py
    version=extract_version(),
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
    # numpy is here to make installing easier... Needs to be at the last position,
    # as thats the first installed with "python setup.py install"
    install_requires=["statsmodels", "matplotlib", "scipy", 
                      "patsy", "pandas", "numpy"],
    classifiers=['Intended Audience :: Science/Research',
                 'Intended Audience :: Developers',
                 'Programming Language :: Python',
                 'Topic :: Software Development',
                 'Topic :: Scientific/Engineering',
                 'Operating System :: Microsoft :: Windows',
                 'Operating System :: POSIX',
                 'Operating System :: Unix',
                 'Operating System :: MacOS',
                 'Programming Language :: Python :: 2',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.3'],
    zip_safe=False)

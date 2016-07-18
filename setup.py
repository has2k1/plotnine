import os
from setuptools import find_packages, setup


def extract_version():
    """
    Extracts version values from the main matplotlib __init__.py and
    returns them as a dictionary.
    """
    with open('ggplotx/__init__.py') as fd:
        for line in fd.readlines():
            if (line.startswith('__version__')):
                exec(line.strip())
    return locals()['__version__']


def get_package_data():
    baseline_images = [
        'tests/baseline_images/%s/*' % x
        for x in os.listdir('ggplotx/tests/baseline_images')]

    return {
        'ggplotx':
        baseline_images +
        [
            'data/*.csv',
            'geoms/*.png'
        ]}

setup(
    name='ggplotx',
    # Increase the version in ggplotx/__init__.py
    version=extract_version(),
    author='Hassan Kibirige',
    author_email='has2k1@gmail.com',
    url='https://github.com/has2k1/ggplotx/',
    license='GPL-2',
    packages=find_packages(),
    package_dir={'ggplotx': 'ggplotx'},
    package_data=get_package_data(),
    description="A grammar of graphics for python",
    # run pandoc --from=markdown --to=rst --output=README.rst README.md
    long_description=open('README.rst').read(),
    # numpy is here to make installing easier... Needs to be at the
    # last position, as that's the first installed with
    # 'python setup.py install'
    install_requires=['six',
                      'statsmodels >= 0.6',
                      'palettable',
                      'matplotlib >= 1.5.1',
                      'scipy',
                      'patsy >= 0.4.1',
                      'pandas >= 0.18.1',
                      'numpy'],
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

import os
from setuptools import find_packages, setup
import versioneer

__author__ = 'Hassan Kibirige'
__email__ = 'has2k1@gmail.com'
__description__ = "A grammar of graphics for python"
__license__ = 'GPL-2'
__url__ = 'https://github.com/has2k1/ggplotx'


def check_dependencies():
    """
    Check for system level dependencies
    """
    pass


def get_required_packages():
    """
    Return required packages

    Plus any version tests and warnings
    """
    install_requires = ['six',
                        'mizani',
                        'matplotlib >= 1.5.1',
                        'numpy',
                        'scipy',
                        'patsy >= 0.4.1',
                        'statsmodels >= 0.6',
                        'pandas >= 0.19.0',
                        ]
    return install_requires


def get_package_data():
    """
    Return package data

    For example:

        {'': ['*.txt', '*.rst'],
         'hello': ['*.msg']}

    means:
        - If any package contains *.txt or *.rst files,
          include them
        - And include any *.msg files found in
          the 'hello' package, too:
    """
    baseline_images = [
        'tests/baseline_images/%s/*' % x
        for x in os.listdir('ggplotx/tests/baseline_images')]
    csv_data = ['data/*.csv']
    package_data = {'ggplotx': baseline_images + csv_data}
    return package_data


if __name__ == '__main__':
    check_dependencies()

    setup(name='ggplotx',
          maintainer=__author__,
          maintainer_email=__email__,
          description=__description__,
          long_description=__doc__,
          license=__license__,
          version=versioneer.get_version(),
          cmdclass=versioneer.get_cmdclass(),
          url=__url__,
          install_requires=get_required_packages(),
          packages=find_packages(),
          package_data=get_package_data(),
          classifiers=['Intended Audience :: Science/Research',
                       'License :: OSI Approved :: GPL-2',
                       'Operating System :: Microsoft :: Windows',
                       'Operating System :: Unix',
                       'Operating System :: MacOS',
                       'Programming Language :: Python :: 2',
                       'Programming Language :: Python :: 3'],
          zip_safe=False)

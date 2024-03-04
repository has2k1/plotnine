"""
This script is run by the Makefile before quarto_build
"""

import re
from importlib.metadata import version as get_version
from pathlib import Path

DOC_DIR = Path(__file__).parent
EXAMPLES_DIR = DOC_DIR / "reference" / "examples"
TUTORIALS_DIR = DOC_DIR / "tutorials"

# The varibables file holds the version
variables_filepath = DOC_DIR / "_variables.yml"
VARIABLES_TPL = """\
version: {version}
"""


def generate_variables_file():
    """
    Generate _variables.yml file in the quartodoc project directory
    """
    # Modifying variables file breaks quarto preview
    if variables_filepath.exists():
        return

    version = get_version("plotnine")

    # The scm-version scheme adds .date suffix to the version
    # if the repo is dirty. For better look while developing,
    # we remove it.
    dirty_pattern = re.compile(r"\.d\d{8}$")
    if dirty_pattern.search(version):
        version = dirty_pattern.sub("", version)

    contents = VARIABLES_TPL.format(version=version)
    variables_filepath.write_text(contents)


if __name__ == "__main__":
    generate_variables_file()

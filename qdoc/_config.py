import re
import shutil
from importlib.metadata import version as get_version
from importlib.resources import files as _files
from pathlib import Path

DOC_DIR = Path(__file__).parent

# The environment file holds the version
ENV_TPL = """\
VERSION={version}
"""


def generate_environment_file():
    """
    Generate _enviroment file in the quartodoc project directory
    """
    version = get_version("plotnine")

    # The scm-version scheme adds .date suffix to the version
    # if the repo is dirty. For better look while developing,
    # we remove it.
    dirty_pattern = re.compile(r"\.d\d{8}$")
    if dirty_pattern.search(version):
        version = dirty_pattern.sub("", version)

    env_filepath = DOC_DIR / "_environment"
    contents = ENV_TPL.format(version=version)
    env_filepath.write_text(contents)


def link_to_examples():
    """
    Copy the plotnine_examples package root
    """
    dest = DOC_DIR / "plotnine_examples"
    if dest.is_dir() and not dest.is_symlink():
        shutil.rmtree(dest)
    src = _files("plotnine_examples")
    shutil.copytree(src, dest)  # type: ignore


if __name__ == "__main__":
    generate_environment_file()
    link_to_examples()

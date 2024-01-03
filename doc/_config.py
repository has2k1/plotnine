"""
This script is run by the Makefile before quarto_build
"""
import hashlib
import re
import shutil
from importlib.metadata import version as get_version
from importlib.resources import files as _files
from pathlib import Path

DOC_DIR = Path(__file__).parent

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


def copy_examples_and_tutorials():
    """
    Copy the examples & tutorials in plotnine_examples
    """

    # NOTE: To avoid confusing the watcher used by "quarto preview",
    # we copy only if the original files are different.
    def same_contents(f1, f2):
        h1 = hashlib.sha256(f1.read_bytes()).hexdigest()
        h2 = hashlib.sha256(f2.read_bytes()).hexdigest()
        return h1 == h2

    def copy(src_dir, dest_dir):
        dest_dir.mkdir(parents=True, exist_ok=True)
        src_files = src_dir.glob("*.ipynb")
        cur_dest_files = dest_dir.glob("*.ipynb")
        new_dest_files = []
        for src in src_files:
            dest = dest_dir / src.name
            new_dest_files.append(dest)
            if dest.exists() and same_contents(src, dest):
                continue
            shutil.copyfile(src, dest)

        # Remove any deleted files
        for dest in set(cur_dest_files).difference(new_dest_files):
            dest.unlink()

    copy(_files("plotnine_examples.examples"), DOC_DIR / "examples")
    copy(_files("plotnine_examples.tutorials"), DOC_DIR / "tutorials")


if __name__ == "__main__":
    generate_variables_file()
    copy_examples_and_tutorials()

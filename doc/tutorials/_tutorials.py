import itertools
from pathlib import Path

import nbformat
from quartodoc.pandoc.blocks import BulletList
from quartodoc.pandoc.inlines import Link

THIS_DIR = Path(__file__).parent
DOC_DIR = THIS_DIR.parent


def get_tutorial_title(filepath: Path) -> str:
    """
    Lookup the title of the notebook
    """
    # The first h1 header
    nb = nbformat.read(filepath.open(), as_version=4)
    markdown_lines = itertools.chain(
        *(c.source.splitlines() for c in nb.cells if c.cell_type == "markdown")
    )
    for line in markdown_lines:
        if line.startswith("# "):
            return line.strip("# ")
    raise ValueError(f"No title found for tutorial: {filepath.name}")


def generate_tutorials_links() -> str:
    """
    Generate links to the tutorials

    Returns
    -------
    :
        Links to tutorial pages in markdown format.
    """
    notebooks = [p for p in THIS_DIR.glob("*.ipynb") if p.stem != "index"]
    link_titles_and_paths = [
        (get_tutorial_title(f), f.relative_to(THIS_DIR)) for f in notebooks
    ]
    links = [Link(t, str(p)) for t, p in link_titles_and_paths]
    return str(BulletList(links))

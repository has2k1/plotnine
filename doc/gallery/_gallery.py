import base64
import io
import itertools
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Generator, Sequence

import nbformat
import PIL.Image
from nbformat.notebooknode import NotebookNode
from quartodoc.pandoc.blocks import Div
from quartodoc.pandoc.components import Attr
from quartodoc.pandoc.inlines import Image, Link

THIS_DIR = Path(__file__).parent
DOC_DIR = THIS_DIR.parent

# String in code cell that creates an image that will be in the gallery
GALLERY_TAG = "# Gallery Plot"
EXAMPLES_DIR = DOC_DIR / "examples"
THUMBNAILS_DIR = Path("thumbnails")
THUMBNAIL_SIZE = (294, 210)

word_and_dashes_pattern = re.compile(r"[^\w-]")


def sanitize_filename(s: str) -> str:
    """
    Clean strings that we make part of filenames
    """
    return word_and_dashes_pattern.sub("-", s).lower()


@dataclass
class GalleryImage:
    """
    Gallery Image
    """

    # The relative path of thumbnail from the gallery
    thumbnail: Path
    title: str
    target: str

    def __str__(self):
        # card, card-header, card-body create bootstrap components
        # https://getbootstrap.com/docs/5.3/components/card/
        #
        # For a responsive layout, use bootstrap grid classes that select
        # for different screen sizes
        # https://getbootstrap.com/docs/5.3/layout/grid/#grid-options
        out_cls = "card g-col-12 g-col-sm-6 g-col-md-4"
        in_cls = "card-header"
        res = Div(
            [
                Div(self.title, Attr(None, in_cls.split())),
                Div(
                    Link(Image(src=self.thumbnail), target=self.target),
                    Attr(None, ["card-body"]),
                ),
            ],
            Attr(None, out_cls.split()),
        )
        return str(res)


def create_thumbnail(output_node: NotebookNode, filepath: Path):
    """
    Create a thumbnail for the gallery

    Parameters
    ----------
    output_node:
        Node containing the output image
    filepath:
        Where to save the created thumbnail on the filesystem
    """
    filepath.parent.mkdir(exist_ok=True, parents=True)
    thumb_size = THUMBNAIL_SIZE[0] * 2, THUMBNAIL_SIZE[1] * 2
    img_str = output_node["data"]["image/png"]
    file = io.BytesIO(base64.decodebytes(img_str.encode()))
    img = PIL.Image.open(file)
    img.thumbnail(thumb_size)
    img.save(filepath)


def get_gallery_image_title(cells: Sequence[NotebookNode]) -> str:
    """
    Return the first level 3 header going backwords
    """
    markdown_lines = itertools.chain(
        *(
            c.source.splitlines()
            for c in cells[::-1]
            if c.cell_type == "markdown"
        )
    )
    for line in markdown_lines:
        if line.startswith("### "):
            return line.strip("# ")
    raise ValueError("No title found for gallery entry")


def get_gallery_images_in_notebook(
    nb_filepath: Path,
) -> Generator[GalleryImage, None, None]:
    """
    Return all gallery images in a notebook
    """
    nb = nbformat.read(nb_filepath.open(), as_version=4)
    nb_cells = nb["cells"]
    notebook_name = nb_filepath.stem

    # The preceeding_cells and the output node that contains
    # an image for the gallery
    gallery_output_nodes = (
        (nb_cells[:ii], node)
        for ii, cell in enumerate(nb_cells)
        if GALLERY_TAG in cell.source
        for node in cell.outputs
        if node.output_type == "display_data"
    )

    for preceeding_cells, output_node in gallery_output_nodes:
        title = get_gallery_image_title(preceeding_cells)
        anchor = sanitize_filename(title)
        relpath = THUMBNAILS_DIR / f"{notebook_name}-{anchor}.png"
        create_thumbnail(output_node, THIS_DIR / relpath)
        target = f"/reference/{notebook_name}.qmd#{anchor}"
        yield GalleryImage(relpath, title, target)


def get_gallery_images(
    nb_filepaths: Sequence[Path],
) -> Generator[GalleryImage, None, None]:
    """
    Return all gallery images
    """
    for filepath in nb_filepaths:
        try:
            yield from get_gallery_images_in_notebook(filepath)
        except Exception as err:
            raise Exception(f"Could not process {filepath}") from err


def generate_gallery() -> str:
    """
    Generate gallery page content

    Returns
    -------
    :
        Gallery in markdown format.

    Notes
    -----
    Calling this function invokes functions with a side-effects.
    """
    notebooks = sorted(
        fp
        for fp in EXAMPLES_DIR.glob("*.ipynb")
        if not fp.name.endswith(".out.ipynb")
    )
    images = (str(img) for img in get_gallery_images(notebooks))
    gallery = Div(list(images), Attr(classes=["gallery", "grid"]))
    return str(gallery)

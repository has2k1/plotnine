# -*- coding: utf-8 -*-
"""
sphinxext.examples_and_gallery

Provides, two directives `include_example` and `gallery`.

How to use the extension
------------------------

1. Create a galley.rst page with a `gallery` directive.
2. Define the path to the notebooks and the notebook filenames
   as `EXPATH` (str), `EXFILES` (set). Together they give
   you the path each notebook file that will converted to ReST.
3. In the Sphinx template used to generate documentation, use::

      .. include_example:: notebook.ipynb

   `notebook.ipynb` should already be executed and should have
   sub-sections i.e (`### This is a section (Header 3)`), and
   they should be unnested. The last output image of each unnested
   sub-section is selected for the gallery. If `###` is nested uder
   `#` or `##`, it will not contribute to the gallery.

How it works
------------

1. Notebooks are converted to ReST.
2. After each doctree is read, the gallery entries are extracted
   and stored on the global `env` object.
3. When the `gallery` doctree is resolved, the gallery node
   is replaced with the gallery entries. They are nodes equivalent
   to::

    .. raw:: html

       <div class="sphx-glr-thumbcontainer" ... >
       ...
       </div>
"""

import os
import re

import nbformat
import sphinx
import nbsphinx
from PIL import Image
from docutils import nodes
from docutils.parsers.rst import Directive
from docutils.parsers.rst.directives.misc import Include
from nbconvert.writers import FilesWriter
from plotnine_examples.examples import EXPATH, EXFILES

# Use build enviroment to get the paths
CUR_PATH = os.path.dirname(os.path.abspath(__file__))
DOC_PATH = os.path.abspath(CUR_PATH + '/..')
RST_PATH = DOC_PATH + '/generated'
IMG_RE = re.compile(r'^\s*\.\. image:: (\w+_examples\/(\w+\.png))')

# Should be about the 11:8 ratio of the default figure size. When this
# value is change, size adjustments should be made in gallery.rst css
thumbnail_size = (196, 140)

entry_html = """\
<div class="sphx-glr-thumbcontainer" {tooltip}>
    <div class="figure">
        <img src="{thumbnail}">
        <p class="caption">
            <span class="caption-text">
                <a class="reference internal" href="{link}">
                    <span class="std std-ref">{title}</span>
                </a>
            </span>
        </p>
    </div>
</div>
""".format


def only_filename(filepath):
    return os.path.basename(filepath)


def only_filename_no_ext(filepath):
    return os.path.splitext(only_filename(filepath))[0]


def has_gallery(builder_name):
    # RTD builder name is not html!
    # We only create a gallery for selected builders
    return builder_name in {'html', 'readthedocs'}


class GalleryEntry:
    def __init__(self, title, section_id, html_link, thumbnail, description):
        self.title = title
        self.description = description
        self.section_id = section_id
        self.html_link = html_link
        self.thumbnail = thumbnail

    @property
    def html(self):
        """
        Return html for a the entry
        """
        # No empty tooltips
        if self.description:
            tooltip = 'tooltip="{}"'.format(self.description)
        else:
            tooltip = ''

        return entry_html(
            title=self.title,
            thumbnail=self.thumbnail,
            link=self.html_link,
            tooltip=tooltip)


class GalleryEntryExtractor:
    """
    Extract gallery entries from a documentaion page.

    The entries extracted are; the last image of every
    section under the examples.

    Parameters
    ----------
    doctree : docutils.nodes.document
        Sphinx doctree that contains Examples
    docname : str, optional
        Name of document from which doctree was created.
    """
    env = None  # Build environment, set at build-inited

    def __init__(self, doctree, docname):
        self.doctree = doctree
        self.docname = docname

    @property
    def htmlfilename(self):
        return '{}.html'.format(self.docname)

    def thumbfilename(self, imgfilename_rst):
        """
        Generate name (without path) for thumbnail
        """
        name = only_filename_no_ext(imgfilename_rst)
        # filename = os.path.join('_images', name+'_thumb.png')
        return name + '_thumb.png'

    def make_thumbnail(self, imgfilename_inrst):
        """
        Make thumbnail and return (html) path to image

        Parameters
        ----------
        imgfilename_rst : rst
            Image filename (relative path), as it appears in the
            ReST file (coverted).
        """
        builddir = self.env.app.outdir

        imgfilename_src = os.path.join(DOC_PATH, imgfilename_inrst)

        thumbfilename = self.thumbfilename(imgfilename_inrst)
        thumbfilename_inhtml = os.path.join('_images', thumbfilename)
        thumbfilename_dest = os.path.join(builddir, '_images', thumbfilename)

        im = Image.open(imgfilename_src)
        im.thumbnail(thumbnail_size)
        im.save(thumbfilename_dest)
        return thumbfilename_inhtml

    def get_entries(self):
        def _get_sections(doctree):
            """
            Return all sections after the 'Examples' section
            """
            # Do not traverse all the sections, only look for those
            # that are siblings of the first node.
            ref_node = doctree[0][0]
            kwargs = dict(descend=False, siblings=True)
            exnode = None  # Examples node
            for section in ref_node.traverse(nodes.section, **kwargs):
                if section[0].astext() == 'Examples':
                    exnode = section
                    break

            if not exnode:
                return

            for section in exnode[0].traverse(nodes.section, **kwargs):
                yield section

        for section in _get_sections(self.doctree):
            section_id = section.attributes['ids'][0]
            section_title = section[0].astext()

            # If an emphasis follows the section, it is the description
            try:
                _node = section[1][0]
            except IndexError:
                _node = None

            if isinstance(_node, nodes.emphasis):
                description = _node.astext()
            else:
                description = ''

            # Last image in the section is used to create the thumbnail
            try:
                image_node = list(section.traverse(nodes.image))[-1]
            except IndexError:
                continue
            else:
                image_filename = image_node.attributes['uri']

            yield GalleryEntry(
                title=section_title,
                section_id=section_id,
                html_link='{}#{}'.format(self.htmlfilename, section_id),
                thumbnail=self.make_thumbnail(image_filename),
                description=description)


def get_rstfilename(nbfilename):
    objname = nbfilename.rstrip('.ipynb')
    return '{}/{}_examples.txt'.format(RST_PATH, objname)


def notebook_to_rst(nbfilename):
    nbfilepath = os.path.join(EXPATH, nbfilename)
    rstfilename = get_rstfilename(nbfilename)
    output_files_dir = only_filename_no_ext(rstfilename)
    metadata_path = os.path.dirname(rstfilename)
    unique_key = nbfilename.rstrip('.ipynb')

    resources = {
        'metadata': {'path': metadata_path},
        'output_files_dir': output_files_dir,
        # Prefix for the output image filenames
        'unique_key': unique_key
    }

    # Read notebook
    with open(nbfilepath, 'r') as f:
        nb = nbformat.read(f, as_version=4)

    # Export
    exporter = nbsphinx.Exporter(execute='never', allow_errors=True)
    (body, resources) = exporter.from_notebook_node(nb, resources)

    # Correct path for the resources
    for filename in list(resources['outputs'].keys()):
        tmp = os.path.join(RST_PATH, filename)
        resources['outputs'][tmp] = resources['outputs'].pop(filename)

    fw = FilesWriter()
    fw.build_directory = RST_PATH
    # Prevent "not in doctree" complains
    resources['output_extension'] = ''
    body = 'Examples\n--------\n' + body
    fw.write(body, resources, notebook_name=rstfilename)


def notebooks_to_rst(app):
    """
    Convert notebooks to rst
    """
    for filename in EXFILES:
        notebook_to_rst(filename)


def extract_gallery_entries(app, doctree):
    if not has_gallery(app.builder.name):
        return

    env = app.env
    docname = env.docname

    if env.has_gallery_entries:
        return

    # So far, only the generated rst can have include
    # examples.
    if not docname.startswith('generated/'):
        return

    gex = GalleryEntryExtractor(doctree, docname)
    env.gallery_entries.extend(list(gex.get_entries()))


def add_entries_to_gallery(app, doctree, docname):
    """
    Add entries to the gallery node

    Should happen when all the doctrees have been read
    and the gallery entries have been collected. i.e at
    doctree-resolved time.
    """
    if docname != 'gallery':
        return

    if not has_gallery(app.builder.name):
        return

    # Find gallery node
    try:
        node = doctree.traverse(gallery)[0]
    except TypeError:
        return

    content = []
    for entry in app.env.gallery_entries:
        raw_html_node = nodes.raw('', text=entry.html, format='html')
        content.append(raw_html_node)

    # Even when content is empty, we want the gallery node replaced
    node.replace_self(content)


class gallery(nodes.General, nodes.Element):
    """
    Empty gallery node
    """
    pass


class Gallery(Directive):
    """
    Gallery

    Thumbnails (html nodes) are added to this directive
    """
    has_content = False
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {}

    def run(self):
        # Simply insert an empty gallery node which will be replaced
        # later, when fill_in_gallery is called.
        return [gallery('')]


class IncludeExamples(Include):
    """
    Directive to include examples for a named object
    """

    option_spec = {
        'module': str
    }

    def run(self):
        nbfilename = self.arguments[0]
        rstfilename = get_rstfilename(nbfilename)

        if not os.path.exists(rstfilename):
            return []

        self.arguments[0] = rstfilename
        return Include.run(self)


def setup_env(app):
    """
    Setup enviroment

    Creates required directory and storage objects (on the
    global enviroment) used by this extension.
    """
    env = app.env
    GalleryEntryExtractor.env = env
    out_imgdir = os.path.join(app.outdir, '_images')

    if not os.path.isdir(RST_PATH):
        os.makedirs(RST_PATH)

    if not os.path.isdir(out_imgdir):
        os.makedirs(out_imgdir)

    if not hasattr(env, 'gallery_entries'):
        # When rebuilding, the pickeled environment has the
        # gallery entries. If caching becomes a problem we
        # can clear the entries at the start of every build.
        # Otherwise, `make clean && make html` should suffice.
        env.gallery_entries = []
        env.has_gallery_entries = False
    else:
        env.has_gallery_entries = True


def visit_gallery_node(self, node):
    pass


def depart_gallery_node(self, node):
    pass


def setup(app):
    app.add_node(
        gallery,
        html=(visit_gallery_node, depart_gallery_node),
        latex=(visit_gallery_node, depart_gallery_node),
        text=(visit_gallery_node, depart_gallery_node),
        man=(visit_gallery_node, depart_gallery_node),
        texinfo=(visit_gallery_node, depart_gallery_node))
    app.add_directive('gallery', Gallery)
    app.add_directive('include_examples', IncludeExamples)
    app.connect('builder-inited', setup_env)
    app.connect('builder-inited', notebooks_to_rst)

    app.connect('doctree-read', extract_gallery_entries)
    app.connect('doctree-resolved', add_entries_to_gallery)

    return {'version': sphinx.__display_version__,
            'parallel_read_safe': True}

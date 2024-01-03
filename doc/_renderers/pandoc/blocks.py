from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import yaml
from quartodoc.pandoc.blocks import (
    Block,
    BlockContent,
    Blocks,
    Header,
    blockcontent_to_str,
)

if TYPE_CHECKING:
    from typing import Any, Optional

    from quartodoc.pandoc.components import Attr
    from quartodoc.pandoc.inlines import Code


@dataclass
class Meta(Block):
    """
    Pandoc meta data block
    """

    table: dict[str, Any]

    def __str__(self):
        yml = yaml.dump(self.table, allow_unicode=True, sort_keys=False)
        return f"---\n{yml}---"


RawHTMLBlockTag_TPL = """\
```{{=html}}
<{tag}{attr}>
```
{content}
```{{=html}}
</{tag}>
```
"""


@dataclass
class RawHTMLBlockTag(Block):
    """
    A Raw HTML Block Tag

    This creates content that is enclosed in an opening and a closing
    pandoc.RawBlock html tag.
    """

    tag: str
    content: Optional[BlockContent] = None
    attr: Optional[Attr] = None

    def __str__(self):
        """
        Return tag content as markdown
        """
        content = blockcontent_to_str(self.content)
        attr = (self.attr and f" {self.attr.html}") or ""
        return RawHTMLBlockTag_TPL.format(
            tag=self.tag, content=content, attr=attr
        )


@dataclass
class RenderedDocObject(Block):
    """
    The rendered parts of an object
    """

    title: Optional[Header] = None
    signature: Optional[Code | str] = None
    body: Optional[BlockContent] = None

    def __str__(self):
        lst = [b for b in (self.title, self.signature, self.body) if b]
        return str(Blocks(lst))
